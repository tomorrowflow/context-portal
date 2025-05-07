import sys
# sys.stderr.write("MINIMAL MAIN.PY: Script started VERY EARLY\\n") # Keeping this one for now
# sys.stderr.flush()

import uvicorn
from fastapi import FastAPI, HTTPException, Request # Added HTTPException, Request
from fastapi.responses import JSONResponse # Removed StreamingResponse
import logging # Added
import json # Added back
import argparse # Added back
from typing import Dict, Any, Optional # Added back
# import asyncio # No longer needed for SSE

# sys.stderr.write("MINIMAL MAIN.PY: Standard imports done.\\n"); sys.stderr.flush()

# Local imports (adjust relative paths if structure changes)
# sys.stderr.write("MINIMAL MAIN.PY: Attempting local imports (try block)...\\n"); sys.stderr.flush()
try:
    # sys.stderr.write("MINIMAL MAIN.PY: Importing .handlers...\\n"); sys.stderr.flush()
    from .handlers import mcp_handlers
    from .core import exceptions
    from .db import database # To ensure cleanup runs if http mode is used
    # sys.stderr.write("MINIMAL MAIN.PY: Local imports in try block successful.\\n"); sys.stderr.flush()
except ImportError:
    # sys.stderr.write("MINIMAL MAIN.PY: ImportError occurred, falling back to except block imports...\\n"); sys.stderr.flush()
    import os
    # sys.stderr.write("MINIMAL MAIN.PY: Imported os in except block.\\n"); sys.stderr.flush()
    # This path needs to be correct for when main.py is run as a script from its own dir
    # For -m src.context_portal_mcp.main, CWD is project root, so src. is findable
    # If running script directly from project root: python src/context_portal_mcp/main.py
    # then __file__ is src/context_portal_mcp/main.py, dirname is src/context_portal_mcp
    # then ../.. is project_root. So this sys.path.insert should be generally okay.
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from src.context_portal_mcp.handlers import mcp_handlers
    from src.context_portal_mcp.core import exceptions
    from src.context_portal_mcp.db import database
    # sys.stderr.write("MINIMAL MAIN.PY: Local imports in except block successful.\\n"); sys.stderr.flush()

sys.stderr.write("MAIN.PY: All imports done.\\n"); sys.stderr.flush() # Simplified prefix
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s') # Added
# sys.stderr.write("MINIMAL MAIN.PY: logging.basicConfig done.\\n"); sys.stderr.flush()
log = logging.getLogger(__name__) # Added
# sys.stderr.write("MINIMAL MAIN.PY: Logger obtained (log global var).\\n"); sys.stderr.flush()

app = FastAPI()

# sys.stderr.write("MINIMAL MAIN.PY: FastAPI app instantiated.\\n")
# sys.stderr.flush()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/mcp") # Standard endpoint for JSON-RPC calls
async def mcp_route_handler(request: Request):
    """Handles JSON-RPC (POST) on /mcp."""
    # POST logic starts here
    log.debug(f"HTTP POST /mcp: Request received from {request.client.host if request.client else 'unknown'}")
    try:
        payload = await request.json()
        log.info(f"Received HTTP JSON-RPC call: {payload}") # Existing INFO log
        log.debug(f"HTTP /mcp: Calling handle_mcp_message with payload: {payload}")
        response_content = handle_mcp_message(payload)
        log.debug(f"HTTP /mcp: handle_mcp_message returned: {response_content}")
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

# --- MCP Message Handling Logic (JSON-RPC 2.0 Compliant) ---
# SSE related code (sse_generator and its uses) has been removed.
# Copied from original full script

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

class JSONRPCErrorCodes:
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR_DEFAULT = -32000
    TOOL_EXECUTION_ERROR = -32001

def handle_mcp_message(message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    request_id = message.get("id")
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
        log.info(f"Handling 'initialize' request with params: {params}")
        server_capabilities_payload = {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {"listChanged": True}},
            "serverInfo": {"name": "ConPort-MinimalTest", "version": "0.0.1-minimal"}
        }
        return create_jsonrpc_success_response(server_capabilities_payload, request_id)
    elif method == "tools/list":
        try:
            log.info("Handling 'tools/list' request.")
            result_payload = mcp_handlers.handle_list_tools(params)
            return create_jsonrpc_success_response(result_payload, request_id)
        except Exception as e:
            log.exception("Unexpected error handling tools/list")
            return create_jsonrpc_error_response(JSONRPCErrorCodes.SERVER_ERROR_DEFAULT, f"Server error: {e}", request_id)
    elif method == "tools/call":
        tool_name = params.get("name")
        tool_arguments = params.get("arguments", {})
        if not tool_name: return create_jsonrpc_error_response(JSONRPCErrorCodes.INVALID_PARAMS, "Missing 'name'", request_id)
        try:
            log.info(f"Dispatching tool call: {tool_name} with args: {tool_arguments}")
            raw_tool_result = mcp_handlers.dispatch_tool(tool_name, tool_arguments)
            json_string_payload = json.dumps(raw_tool_result)
            mcp_text_content = {"type": "text", "text": json_string_payload}
            formatted_result_payload = {"content": [mcp_text_content], "isError": False}
            return create_jsonrpc_success_response(formatted_result_payload, request_id)
        except NotImplementedError as e: return create_jsonrpc_error_response(JSONRPCErrorCodes.METHOD_NOT_FOUND, str(e), request_id)
        except exceptions.ToolArgumentError as e: return create_jsonrpc_error_response(JSONRPCErrorCodes.INVALID_PARAMS, str(e), request_id)
        except exceptions.ContextPortalError as e: return create_jsonrpc_error_response(JSONRPCErrorCodes.TOOL_EXECUTION_ERROR, str(e), request_id, data={"error_type": e.__class__.__name__})
        except Exception as e:
            log.exception(f"Unexpected error dispatching tool {tool_name}")
            return create_jsonrpc_error_response(JSONRPCErrorCodes.INTERNAL_ERROR, f"Internal server error: {e}", request_id)
    else:
        log.warning(f"Method not found: {method}")
        return create_jsonrpc_error_response(JSONRPCErrorCodes.METHOD_NOT_FOUND, f"Method not found: {method}", request_id)

def run_stdio_mode():
    """Runs the server in stdio mode, reading/writing JSON-RPC 2.0 lines."""
    # Ensure log is defined (it should be from global scope)
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
                # Ensure create_jsonrpc_error_response and JSONRPCErrorCodes are defined
                response = create_jsonrpc_error_response(JSONRPCErrorCodes.PARSE_ERROR, f"Invalid JSON received: {line}", None) 
            else:
                # Ensure handle_mcp_message is defined
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
        # Ensure database is imported and has close_all_connections
        if 'database' in globals() and hasattr(database, 'close_all_connections'):
            database.close_all_connections() 
        else:
            sys.stderr.write("MINIMAL MAIN.PY: STDERR - 'database' module or 'close_all_connections' not found for stdio shutdown.\\n"); sys.stderr.flush()
# sys.stderr.write("MINIMAL MAIN.PY: Helper functions and all routes defined. Approaching __main__ check.\\n")
# sys.stderr.flush()
sys.stderr.write(f"MAIN.PY: Value of __name__ is: '{__name__}'\\n"); sys.stderr.flush() # Simplified prefix

if __name__ == "__main__":
    sys.stderr.write("MAIN.PY: Inside __main__ block.\\n"); sys.stderr.flush() # Simplified prefix
    
    # Restoring full argparse
    # sys.stderr.write(f"MINIMAL MAIN.PY: sys.argv is: {sys.argv}\\n"); sys.stderr.flush() # Too verbose for manual run
    parser = argparse.ArgumentParser(description="Context Portal MCP Server")
    # sys.stderr.write("MINIMAL MAIN.PY: After ArgumentParser, before add_argument calls.\\n"); sys.stderr.flush()
    parser.add_argument(
        "--mode",
        choices=["stdio"], # Removed "http"
        default="stdio",
        help="Server communication mode (default: stdio)"
    )
    # --host and --port arguments are removed as HTTP mode is disabled
    # sys.stderr.write("MINIMAL MAIN.PY: After add_argument calls, before parse_args.\\n"); sys.stderr.flush()
    args = parser.parse_args()
    sys.stderr.write(f"MAIN.PY: Parsed args: mode={args.mode}\\n"); sys.stderr.flush() # Simplified prefix

    # Mode dispatch logic
    if args.mode == "stdio":
        sys.stderr.write("MAIN.PY: Mode is stdio. Calling run_stdio_mode().\\n"); sys.stderr.flush()
        run_stdio_mode()
    # Removed http mode handling
    # else: # This case should not be reached if choices are restricted
    #     log.error(f"Invalid mode: {args.mode}. Exiting.")
    #     sys.stderr.write(f"MAIN.PY: Invalid mode '{args.mode}'. Exiting.\\n"); sys.stderr.flush()
    #     sys.exit(1) # Exit if mode is somehow invalid despite choices
else: # This else is for if __name__ != "__main__"
    sys.stderr.write(f"MAIN.PY: __name__ is '{__name__}', not '__main__'. Server startup logic in __main__ block will be skipped.\\n"); sys.stderr.flush()
# Add definition for run_stdio_mode if it was stripped in "minimal" version
# For safety, let's ensure it's defined before it's potentially called.
# It should be defined before the `if __name__ == "__main__":` block.
# The diff tool might struggle with large insertions. I'll try to place it before __main__.
# This will be a separate apply_diff if needed, or assume it's there from previous full script copy.
# For now, this diff focuses on the __main__ block.
# The `run_stdio_mode` was defined from lines 267-297 in the full script.
# I will add it before the `if __name__ == "__main__":` block.
# This requires a new SEARCH block.
# Let's find where to insert run_stdio_mode. Before line 196 (the current stderr print before __main__ check)

# This diff is getting too complex. I will do run_stdio_mode separately if needed.
# The current diff only modifies the __main__ block.
# The `run_stdio_mode` function was part of the "helper functions" I said were restored.
# Let's verify `run_stdio_mode` is indeed present from the previous `read_file` (user timestamp 10:33 PM, my response 10:45 PM).
# Yes, lines 267-297 in that full read was `def run_stdio_mode(): ...`
# The current read (user timestamp 10:48 PM) is truncated at line 225.
# I need to re-read the full current main.py to correctly place run_stdio_mode if it's missing
# or to confirm its location.

# For now, I will assume run_stdio_mode is defined from the previous step where I added helpers.
# The key change is restoring full argparse in __main__.
# And adding a stderr print before calling run_stdio_mode.
# And ensuring the http elif uses args.host/args.port.
# And adding the final else for invalid args.mode.

# The original args.mode dispatch was:
# if args.mode == "stdio": run_stdio_mode()
# elif args.mode == "http": log.info(...); uvicorn.run(...)
# else: log.error(...); sys.exit(1)
# This needs to be restored.

# The diff above correctly sets up argparse and the if/elif for stdio/http.
# It's missing the final `else` for invalid mode from the original script.
# And it's missing the `run_stdio_mode` definition if it was stripped.
# The current read is truncated. I will proceed with this diff for the __main__ block,
# and then re-evaluate based on the next full read_file.
# The current diff changes lines 202-209 and 212.
# It also needs to add the final `else: log.error(...); sys.exit(1)`

# Let's refine the diff for the __main__ block to be more complete.
# Original __main__ block (from a full version) was lines 302-363.
# Current __main__ block in the read file (truncated) starts at line 201.
# I will replace the entire current `if __name__ == "__main__":` block and its `else`.

# sys.stderr.write("MINIMAL MAIN.PY: Script end reached.\\n") # Commenting out
# sys.stderr.flush()