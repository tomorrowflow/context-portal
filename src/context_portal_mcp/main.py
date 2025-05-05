"""Main application entry point for the Context Portal MCP server."""

import sys
import json
import argparse
import logging
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn

# Local imports (adjust relative paths if structure changes)
try:
    from .handlers import mcp_handlers
    from .core import exceptions
    from .db import database # To ensure cleanup runs if http mode is used
except ImportError:
    # Allow running script directly for testing/debugging
    # This is a common pattern but might need adjustment based on final structure
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from src.context_portal_mcp.handlers import mcp_handlers
    from src.context_portal_mcp.core import exceptions
    from src.context_portal_mcp.db import database


# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# --- FastAPI App (for HTTP mode) ---
app = FastAPI(title="Context Portal MCP Server")

@app.post("/mcp/call")
async def mcp_tool_call(request: Request):
    """Endpoint to handle MCP tool calls via HTTP POST."""
    try:
        payload = await request.json()
        log.info(f"Received HTTP MCP call: {payload}")
        result = handle_mcp_message(payload)
        log.info(f"Sending HTTP MCP response: {result}")
        return JSONResponse(content=result)
    except json.JSONDecodeError:
        log.error("HTTP Request body is not valid JSON")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except exceptions.ContextPortalError as e:
        log.error(f"Error handling HTTP MCP call: {e}")
        # Return error in MCP format
        error_response = create_mcp_error_response(str(e))
        return JSONResponse(content=error_response, status_code=400) # Or 500 depending on error type
    except Exception as e:
        log.exception("Unexpected error handling HTTP MCP call")
        error_response = create_mcp_error_response(f"Unexpected server error: {e}")
        return JSONResponse(content=error_response, status_code=500)


# --- MCP Message Handling Logic ---

def create_mcp_response(result_data: Dict[str, Any]) -> Dict[str, Any]:
    """Formats a successful MCP response."""
    return {
        "protocol": "mcp",
        "type": "response",
        "status": "success",
        "payload": result_data
    }

def create_mcp_error_response(error_message: str, error_type: str = "ToolExecutionError") -> Dict[str, Any]:
    """Formats an MCP error response."""
    return {
        "protocol": "mcp",
        "type": "response",
        "status": "error",
        "payload": {
            "error_type": error_type,
            "message": error_message
        }
    }

def handle_mcp_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """Parses and handles a single incoming MCP message dictionary."""
    if message.get("protocol") != "mcp" or message.get("type") != "request":
        return create_mcp_error_response("Invalid MCP message format", "InvalidRequestError")

    tool_name = message.get("tool_name")
    arguments = message.get("arguments", {})

    if not tool_name:
        return create_mcp_error_response("Missing 'tool_name' in request", "InvalidRequestError")
    if not isinstance(arguments, dict):
         return create_mcp_error_response("'arguments' must be a dictionary", "InvalidRequestError")

    try:
        log.info(f"Dispatching tool: {tool_name} with args: {arguments}")
        result_payload = mcp_handlers.dispatch_tool(tool_name, arguments)
        return create_mcp_response(result_payload)
    except NotImplementedError as e:
        log.warning(f"Tool not implemented: {tool_name}")
        return create_mcp_error_response(str(e), "ToolNotImplementedError")
    except exceptions.ToolArgumentError as e:
         log.error(f"Tool argument error: {e}")
         return create_mcp_error_response(str(e), "ToolArgumentError")
    except exceptions.ContextPortalError as e:
        log.error(f"Context Portal specific error: {e}")
        return create_mcp_error_response(str(e), e.__class__.__name__) # Use specific exception name
    except Exception as e:
        log.exception(f"Unexpected error dispatching tool {tool_name}")
        return create_mcp_error_response(f"Unexpected error: {e}", "ServerError")


# --- Stdio Mode Logic ---

def run_stdio_mode():
    """Runs the server in stdio mode, reading/writing JSON lines."""
    log.info("Starting Context Portal MCP Server in stdio mode...")
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue # Skip empty lines

            log.debug(f"Received stdio line: {line}")
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                log.error(f"Failed to decode JSON: {line}")
                response = create_mcp_error_response(f"Invalid JSON received: {line}", "InvalidRequestError")
            else:
                response = handle_mcp_message(message)

            response_line = json.dumps(response)
            log.debug(f"Sending stdio response: {response_line}")
            print(response_line, flush=True) # Ensure output is sent immediately

    except KeyboardInterrupt:
        log.info("Stdio mode interrupted by user.")
    except Exception as e:
        log.exception("Unexpected error in stdio mode")
    finally:
        log.info("Stdio mode shutting down.")
        database.close_all_connections() # Ensure DB connections closed


# --- Main Execution ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Context Portal MCP Server")
    parser.add_argument(
        "--mode",
        choices=["stdio", "http"],
        default="stdio",
        help="Server communication mode (default: stdio)"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for HTTP server (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8123, # Default port mentioned in proposal
        help="Port for HTTP server (default: 8123)"
    )
    args = parser.parse_args()

    if args.mode == "stdio":
        run_stdio_mode()
    elif args.mode == "http":
        log.info(f"Starting Context Portal MCP Server in HTTP mode on {args.host}:{args.port}...")
        # Note: Uvicorn handles its own shutdown procedure, atexit in database.py should cover DB closure.
        uvicorn.run(app, host=args.host, port=args.port)
    else:
         # Should not happen due to choices constraint, but good practice
         log.error(f"Invalid mode specified: {args.mode}")
         sys.exit(1)