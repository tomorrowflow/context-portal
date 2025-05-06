"""Main application entry point for the Context Portal MCP server."""

import sys
import json
import argparse
import logging
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn
import asyncio # For SSE keep-alive/delay

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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') # Revert level to INFO
log = logging.getLogger(__name__)

# --- FastAPI App (for HTTP mode) ---
app = FastAPI(title="Context Portal MCP Server")

@app.post("/mcp") # Standard endpoint for JSON-RPC calls
async def mcp_json_rpc_call(request: Request):
    """Endpoint to handle JSON-RPC 2.0 calls via HTTP POST."""
    try:
        payload = await request.json()
        log.info(f"Received HTTP JSON-RPC call: {payload}")
        response_content = handle_mcp_message(payload)
        if response_content:
            log.info(f"Sending HTTP JSON-RPC response: {response_content}")
            return JSONResponse(content=response_content)
        else:
            # For notifications, typically return HTTP 204 No Content or 202 Accepted
            log.info("Processed notification, no content to return.")
            return JSONResponse(content=None, status_code=204)
    except json.JSONDecodeError:
        log.error("HTTP Request body is not valid JSON")
        # JSON-RPC Parse Error
        error_resp = create_jsonrpc_error_response(JSONRPCErrorCodes.PARSE_ERROR, "Parse error", None)
        return JSONResponse(content=error_resp, status_code=400)
    except Exception as e: # Catch-all for unexpected errors during handle_mcp_message or FastAPI processing
        log.exception("Unexpected error handling HTTP JSON-RPC call")
        # Attempt to get request_id if payload was parsed, otherwise None
        request_id = None
        try:
            if 'payload' not in locals(): # if payload failed to parse
                 payload = await request.json() # try again, might fail
            request_id = payload.get("id")
        except: #  Ignore if we can't get ID during an error
            pass
        error_resp = create_jsonrpc_error_response(JSONRPCErrorCodes.INTERNAL_ERROR, f"Internal server error: {e}", request_id)
        return JSONResponse(content=error_resp, status_code=500)


# --- SSE Endpoint ---

async def sse_generator():
    """Async generator for sending SSE messages."""
    try:
        # Send an initial event to confirm connection
        initial_event = {"event": "mcp_connected", "data": json.dumps({"message": "Context Portal Server Connected via SSE"})}
        yield f"event: {initial_event['event']}\ndata: {initial_event['data']}\n\n"
        log.info("SSE client connected.")
        # The client should use the JSON-RPC endpoint (e.g., /mcp via POST)
        # to send an 'initialize' request, then a 'tools/list' request.
        # Proactively sending tools here might not align with standard client behavior
        # and could be removed if the client is expected to follow the full JSON-RPC flow.
        # For now, let's comment out the proactive tool list push on SSE connect.
        # try:
        #     tool_list_payload = mcp_handlers.handle_list_tools({})
        #     log.debug(f"Generated tool list payload for SSE: {tool_list_payload}")
        #     tool_list_event = {"event": "mcp_tools_update", "data": json.dumps(tool_list_payload)}
        #     yield f"event: {tool_list_event['event']}\ndata: {tool_list_event['data']}\n\n"
        #     log.info("Sent initial tool list via SSE using 'mcp_tools_update' event. (This may be removed later)")
        # except Exception as e:
        #     log.error(f"Failed to get or send initial tool list via SSE: {e}")
        #     error_event = {"event": "mcp_error", "data": json.dumps({"error": "Failed to retrieve tool list on SSE connect"})}
        #     yield f"event: {error_event['event']}\ndata: {error_event['data']}\n\n"

        # Keep connection alive - send comments periodically
        while True:
            await asyncio.sleep(15) # Send a comment every 15 seconds
            yield ": keep-alive\n\n"
    except asyncio.CancelledError:
        log.info("SSE client disconnected.")
        raise # Re-raise CancelledError to ensure FastAPI cleans up
    except Exception as e:
        log.error(f"Error in SSE generator: {e}")
        # Optionally send an error event before closing
        error_event = {"event": "mcp_error", "data": json.dumps({"error": "Internal server error in SSE stream"})}
        yield f"event: {error_event['event']}\ndata: {error_event['data']}\n\n"


@app.get("/mcp/sse")
async def sse_endpoint():
    """Endpoint for establishing Server-Sent Events (SSE) connection."""
    return StreamingResponse(sse_generator(), media_type="text/event-stream")


# --- MCP Message Handling Logic (JSON-RPC 2.0 Compliant) ---

def create_jsonrpc_success_response(result_data: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
    """Formats a successful JSON-RPC 2.0 response."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result_data
    }

def create_jsonrpc_error_response(code: int, message_text: str, request_id: Any, data: Optional[Any] = None) -> Dict[str, Any]:
    """Formats a JSON-RPC 2.0 error response."""
    error_obj = {"code": code, "message": message_text}
    if data is not None:
        error_obj["data"] = data
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": error_obj
    }

# Standard JSON-RPC Error Codes
class JSONRPCErrorCodes:
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    # Custom server errors can range from -32000 to -32099
    SERVER_ERROR_DEFAULT = -32000
    TOOL_EXECUTION_ERROR = -32001 # Example custom error

def handle_mcp_message(message: Dict[str, Any]) -> Optional[Dict[str, Any]]: # Can return None for notifications
    """Parses and handles a single incoming JSON-RPC 2.0 message dictionary."""
    request_id = message.get("id") # Can be null for notifications

    if message.get("jsonrpc") != "2.0":
        return create_jsonrpc_error_response(JSONRPCErrorCodes.INVALID_REQUEST, "Invalid JSON-RPC version", request_id)

    method = message.get("method")
    params = message.get("params", {})

    if not method:
        return create_jsonrpc_error_response(JSONRPCErrorCodes.INVALID_REQUEST, "Missing 'method'", request_id)
    if not isinstance(params, dict):
         return create_jsonrpc_error_response(JSONRPCErrorCodes.INVALID_REQUEST, "'params' must be an object", request_id)

    log.info(f"Received JSON-RPC method: {method}, params: {params}, id: {request_id}")

    if method == "initialize":
        # Params for initialize typically include clientInfo, capabilities, protocolVersion
        log.info(f"Handling 'initialize' request with params: {params}")
        server_capabilities_payload = {
            "protocolVersion": "2024-11-05", # Align with MCP spec version
            "capabilities": {
                "tools": {"listChanged": True},
                "resources": {"listChanged": True, "subscribe": True}, # Example
                "prompts": {"listChanged": True}, # Example
                "logging": {} # Example
            },
            "serverInfo": {
                "name": "Context Portal MCP (ConPort)",
                "version": "0.1.0" # TODO: Make this dynamic
            }
            # "instructions": "Optional instructions for the client" # As per spec
        }
        return create_jsonrpc_success_response(server_capabilities_payload, request_id)

    elif method == "notifications/initialized" or method == "initialized": # Handle client initialized notification
        log.info(f"Received '{method}' notification from client. No response needed.")
        return None # Notifications do not have responses

    elif method == "tools/list":
        try:
            log.info("Handling 'tools/list' request.")
            # `params` for tools/list might contain a "cursor" for pagination,
            # mcp_handlers.handle_list_tools currently ignores arguments.
            result_payload = mcp_handlers.handle_list_tools(params)
            return create_jsonrpc_success_response(result_payload, request_id)
        except Exception as e:
            log.exception("Unexpected error handling tools/list")
            return create_jsonrpc_error_response(JSONRPCErrorCodes.SERVER_ERROR_DEFAULT, f"Server error: {e}", request_id)

    elif method == "tools/call":
        tool_name = params.get("name")
        tool_arguments = params.get("arguments", {})
        if not tool_name:
            return create_jsonrpc_error_response(JSONRPCErrorCodes.INVALID_PARAMS, "Missing 'name' in tools/call params", request_id)
        if not isinstance(tool_arguments, dict):
            return create_jsonrpc_error_response(JSONRPCErrorCodes.INVALID_PARAMS, "'arguments' in tools/call params must be an object", request_id)
        
        try:
            log.info(f"Dispatching tool call: {tool_name} with args: {tool_arguments}")
            raw_tool_result = mcp_handlers.dispatch_tool(tool_name, tool_arguments)

            # Format the raw tool result into an MCP TextContent block containing a JSON string.
            # All tools in this server currently return JSON-serializable dicts or lists of dicts.
            try:
                json_string_payload = json.dumps(raw_tool_result)
                mcp_text_content = {"type": "text", "text": json_string_payload}
            except TypeError as te:
                log.error(f"Failed to serialize tool result to JSON for {tool_name}: {te}")
                # Fallback or error reporting if serialization fails
                mcp_text_content = {"type": "text", "text": f"Error: Could not serialize result for {tool_name}."}

            # The standard MCP tools/call result structure
            formatted_result_payload = {
                "content": [mcp_text_content],
                "isError": False # Assuming success if no exception was caught by this point from dispatch_tool
            }
            return create_jsonrpc_success_response(formatted_result_payload, request_id)
        except NotImplementedError as e:
            log.warning(f"Tool not implemented: {tool_name}")
            return create_jsonrpc_error_response(JSONRPCErrorCodes.METHOD_NOT_FOUND, str(e), request_id)
        except exceptions.ToolArgumentError as e:
            log.error(f"Tool argument error: {e}")
            return create_jsonrpc_error_response(JSONRPCErrorCodes.INVALID_PARAMS, str(e), request_id)
        except exceptions.ContextPortalError as e: # Custom app errors
            log.error(f"Context Portal specific error: {e}")
            # Map to a generic server error or a specific custom error code if defined
            return create_jsonrpc_error_response(JSONRPCErrorCodes.TOOL_EXECUTION_ERROR, str(e), request_id, data={"error_type": e.__class__.__name__})
        except Exception as e:
            log.exception(f"Unexpected error dispatching tool {tool_name}")
            return create_jsonrpc_error_response(JSONRPCErrorCodes.INTERNAL_ERROR, f"Internal server error: {e}", request_id)
    else:
        log.warning(f"Method not found: {method}")
        return create_jsonrpc_error_response(JSONRPCErrorCodes.METHOD_NOT_FOUND, f"Method not found: {method}", request_id)


# --- Stdio Mode Logic ---

def run_stdio_mode():
    """Runs the server in stdio mode, reading/writing JSON-RPC 2.0 lines."""
    log.info("Starting Context Portal MCP Server in stdio mode (JSON-RPC 2.0)... Waiting for messages.")
    # No initial message; server waits for client's initialize request.
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
                response = create_jsonrpc_error_response(JSONRPCErrorCodes.PARSE_ERROR, f"Invalid JSON received: {line}", None) # No ID if parse error
            else:
                response = handle_mcp_message(message)

            if response: # handle_mcp_message can return None for notifications
                response_line = json.dumps(response)
                log.debug(f"Sending stdio JSON-RPC response: {response_line}")
                print(response_line, flush=True)

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