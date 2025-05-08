import sys
import uvicorn
from fastapi import FastAPI
import logging
import argparse
from typing import Dict, Any, Optional, AsyncIterator, List # Added AsyncIterator and List
from contextlib import asynccontextmanager # Added

# MCP SDK imports
from mcp.server.fastmcp import FastMCP, Context as MCPContext # Renamed Context to avoid clash
# ServerInfo from mcp.server.models was an incorrect import path.
# FastMCP takes name directly. Version for serverInfo capability is often handled by the SDK.

# Local imports
try:
    from .handlers import mcp_handlers # We will adapt these
    from .db import database, models # models for tool argument types
    from .core import exceptions # For custom exceptions if FastMCP doesn't map them
except ImportError:
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from src.context_portal_mcp.handlers import mcp_handlers
    from src.context_portal_mcp.db import database, models
    from src.context_portal_mcp.core import exceptions

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
log = logging.getLogger(__name__)

# --- Lifespan Management for FastMCP ---
@asynccontextmanager
async def conport_lifespan(server: FastMCP) -> AsyncIterator[None]:
    """Manage application lifecycle for ConPort."""
    log.info("ConPort FastMCP server lifespan starting.")
    # Database initialization is handled by get_db_connection on first access per workspace.
    # No explicit global startup needed for DB here unless we want to pre-connect to a default.
    try:
        yield None  # Server runs
    finally:
        log.info("ConPort FastMCP server lifespan shutting down. Closing all DB connections.")
        database.close_all_connections()

# --- FastMCP Server Instance ---
# Version from pyproject.toml would be ideal here, or define centrally
CONPORT_VERSION = "0.1.0"

conport_mcp = FastMCP(
    name="ConPort", # Pass name directly
    # The version for the serverInfo capability response will be handled by FastMCP,
    # potentially from package metadata or a default.
    lifespan=conport_lifespan
)

# --- FastAPI App ---
# The FastAPI app will be the main ASGI app, and FastMCP will be mounted onto it.
# We keep our own FastAPI app instance in case we want to add other non-MCP HTTP endpoints later.
app = FastAPI(title="ConPort MCP Server Wrapper", version=CONPORT_VERSION)

# --- Adapt and Register Tools with FastMCP ---
# This section replaces the old mcp_handlers.dispatch_tool and TOOL_HANDLERS

# Example for get_product_context
# Note: The original handlers returned the full JSON-RPC response.
# FastMCP tool handlers should return the direct result data.
# FastMCP uses type hints on the handler for input validation if no schema is provided.
# We use our Pydantic models as input_schema for robust validation.

@conport_mcp.tool(name="get_product_context")
async def tool_get_product_context(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> Dict[str, Any]:
    sys.stderr.write(f"MAIN.PY: tool_get_product_context received raw_args_from_fastmcp: type={type(raw_args_from_fastmcp)}, value={raw_args_from_fastmcp}\\n"); sys.stderr.flush()
    try:
        # raw_args_from_fastmcp directly contains the arguments e.g. {'workspace_id': '...'}
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        if workspace_id_val is None:
            log.error(f"CRITICAL: 'workspace_id' not found in raw_args_from_fastmcp for get_product_context. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id' in arguments for get_product_context")
        pydantic_args = models.GetContextArgs(workspace_id=workspace_id_val)
        return mcp_handlers.handle_get_product_context(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in get_product_context handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for get_product_context: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing get_product_context: {type(e).__name__}")

@conport_mcp.tool(name="update_product_context")
async def tool_update_product_context(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> Dict[str, Any]:
    sys.stderr.write(f"MAIN.PY: tool_update_product_context received raw_args_from_fastmcp: type={type(raw_args_from_fastmcp)}, value={raw_args_from_fastmcp}\\n"); sys.stderr.flush()
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        content_val = raw_args_from_fastmcp.get("content")
        if workspace_id_val is None or content_val is None: # Check for both required fields
            log.error(f"CRITICAL: Missing 'workspace_id' or 'content' in raw_args_from_fastmcp for update_product_context. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id' or 'content' in arguments for update_product_context")
        pydantic_args = models.UpdateContextArgs(workspace_id=workspace_id_val, content=content_val)
        return mcp_handlers.handle_update_product_context(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in update_product_context handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for update_product_context: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing update_product_context: {type(e).__name__}")

@conport_mcp.tool(name="get_active_context")
async def tool_get_active_context(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> Dict[str, Any]:
    sys.stderr.write(f"MAIN.PY: tool_get_active_context received raw_args_from_fastmcp: type={type(raw_args_from_fastmcp)}, value={raw_args_from_fastmcp}\\n"); sys.stderr.flush()
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        if workspace_id_val is None:
            log.error(f"CRITICAL: 'workspace_id' not found in raw_args_from_fastmcp for get_active_context. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id' in arguments for get_active_context")
        pydantic_args = models.GetContextArgs(workspace_id=workspace_id_val)
        return mcp_handlers.handle_get_active_context(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in get_active_context handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for get_active_context: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing get_active_context: {type(e).__name__}")

@conport_mcp.tool(name="update_active_context")
async def tool_update_active_context(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> Dict[str, Any]:
    sys.stderr.write(f"MAIN.PY: tool_update_active_context received raw_args_from_fastmcp: type={type(raw_args_from_fastmcp)}, value={raw_args_from_fastmcp}\\n"); sys.stderr.flush()
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        content_val = raw_args_from_fastmcp.get("content")
        if workspace_id_val is None or content_val is None:
            log.error(f"CRITICAL: Missing 'workspace_id' or 'content' in raw_args_from_fastmcp for update_active_context. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id' or 'content' in arguments for update_active_context")
        pydantic_args = models.UpdateContextArgs(workspace_id=workspace_id_val, content=content_val)
        return mcp_handlers.handle_update_active_context(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in update_active_context handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for update_active_context: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing update_active_context: {type(e).__name__}")

@conport_mcp.tool(name="log_decision")
async def tool_log_decision(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> Dict[str, Any]:
    sys.stderr.write(f"MAIN.PY: tool_log_decision received raw_args_from_fastmcp: type={type(raw_args_from_fastmcp)}, value={raw_args_from_fastmcp}\\n"); sys.stderr.flush()
    try:
        # Extract all fields for LogDecisionArgs
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        summary_val = raw_args_from_fastmcp.get("summary")
        if workspace_id_val is None or summary_val is None: # Required fields
            log.error(f"CRITICAL: Missing 'workspace_id' or 'summary' for log_decision. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id' or 'summary' in arguments for log_decision")
        pydantic_args = models.LogDecisionArgs(
            workspace_id=workspace_id_val,
            summary=summary_val,
            rationale=raw_args_from_fastmcp.get("rationale"), # Optional
            implementation_details=raw_args_from_fastmcp.get("implementation_details") # Optional
        )
        
        return mcp_handlers.handle_log_decision(pydantic_args) # Pass Pydantic model
    except exceptions.ContextPortalError as e: # Catch errors from the handler
        log.error(f"Error in log_decision handler: {e}")
        raise
    except Exception as e: # Catch other errors like Pydantic validation or the ValueError above
        log.error(f"Error processing args for log_decision: {e}. Received raw: {raw_args_from_fastmcp}")
        # Re-raise; FastMCP should convert this to an internal server error for the client.
        # Avoids exposing too much detail unless FastMCP already does that.
        raise exceptions.ContextPortalError(f"Server error processing log_decision: {type(e).__name__}")

@conport_mcp.tool(name="get_decisions")
async def tool_get_decisions(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> List[Dict[str, Any]]:
    sys.stderr.write(f"MAIN.PY: tool_get_decisions received raw_args_from_fastmcp: type={type(raw_args_from_fastmcp)}, value={raw_args_from_fastmcp}\\n"); sys.stderr.flush()
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        if workspace_id_val is None:
            log.error(f"CRITICAL: 'workspace_id' not found for get_decisions. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id' in arguments for get_decisions")
        pydantic_args = models.GetDecisionsArgs(
            workspace_id=workspace_id_val,
            limit=raw_args_from_fastmcp.get("limit") # Optional
        )
        return mcp_handlers.handle_get_decisions(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in get_decisions handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for get_decisions: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing get_decisions: {type(e).__name__}")

@conport_mcp.tool(name="search_decisions_fts")
async def tool_search_decisions_fts(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> List[Dict[str, Any]]:
    sys.stderr.write(f"MAIN.PY: tool_search_decisions_fts received raw_args_from_fastmcp: type={type(raw_args_from_fastmcp)}, value={raw_args_from_fastmcp}\\n"); sys.stderr.flush()
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        query_term_val = raw_args_from_fastmcp.get("query_term")
        if workspace_id_val is None or query_term_val is None:
            log.error(f"CRITICAL: Missing 'workspace_id' or 'query_term' for search_decisions_fts. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id' or 'query_term' in arguments for search_decisions_fts")
        pydantic_args = models.SearchDecisionsArgs(
            workspace_id=workspace_id_val,
            query_term=query_term_val,
            limit=raw_args_from_fastmcp.get("limit") # Optional
        )
        return mcp_handlers.handle_search_decisions_fts(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in search_decisions_fts handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for search_decisions_fts: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing search_decisions_fts: {type(e).__name__}")

@conport_mcp.tool(name="log_progress")
async def tool_log_progress(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> Dict[str, Any]:
    sys.stderr.write(f"MAIN.PY: tool_log_progress received raw_args_from_fastmcp: type={type(raw_args_from_fastmcp)}, value={raw_args_from_fastmcp}\\n"); sys.stderr.flush()
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        status_val = raw_args_from_fastmcp.get("status")
        description_val = raw_args_from_fastmcp.get("description")
        if workspace_id_val is None or status_val is None or description_val is None:
            log.error(f"CRITICAL: Missing required fields for log_progress. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id', 'status', or 'description' in arguments for log_progress")
        pydantic_args = models.LogProgressArgs(
            workspace_id=workspace_id_val,
            status=status_val,
            description=description_val,
            parent_id=raw_args_from_fastmcp.get("parent_id") # Optional
        )
        return mcp_handlers.handle_log_progress(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in log_progress handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for log_progress: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing log_progress: {type(e).__name__}")

@conport_mcp.tool(name="get_progress")
async def tool_get_progress(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> List[Dict[str, Any]]:
    sys.stderr.write(f"MAIN.PY: tool_get_progress received raw_args_from_fastmcp: type={type(raw_args_from_fastmcp)}, value={raw_args_from_fastmcp}\\n"); sys.stderr.flush()
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        if workspace_id_val is None:
            log.error(f"CRITICAL: 'workspace_id' not found for get_progress. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id' in arguments for get_progress")
        pydantic_args = models.GetProgressArgs(
            workspace_id=workspace_id_val,
            status_filter=raw_args_from_fastmcp.get("status_filter"), # Optional
            parent_id_filter=raw_args_from_fastmcp.get("parent_id_filter"), # Optional
            limit=raw_args_from_fastmcp.get("limit") # Optional
        )
        return mcp_handlers.handle_get_progress(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in get_progress handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for get_progress: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing get_progress: {type(e).__name__}")

@conport_mcp.tool(name="log_system_pattern")
async def tool_log_system_pattern(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> Dict[str, Any]:
    sys.stderr.write(f"MAIN.PY: tool_log_system_pattern received raw_args_from_fastmcp: type={type(raw_args_from_fastmcp)}, value={raw_args_from_fastmcp}\\n"); sys.stderr.flush()
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        name_val = raw_args_from_fastmcp.get("name")
        if workspace_id_val is None or name_val is None:
            log.error(f"CRITICAL: Missing 'workspace_id' or 'name' for log_system_pattern. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id' or 'name' in arguments for log_system_pattern")
        pydantic_args = models.LogSystemPatternArgs(
            workspace_id=workspace_id_val,
            name=name_val,
            description=raw_args_from_fastmcp.get("description") # Optional
        )
        return mcp_handlers.handle_log_system_pattern(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in log_system_pattern handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for log_system_pattern: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing log_system_pattern: {type(e).__name__}")

@conport_mcp.tool(name="get_system_patterns")
async def tool_get_system_patterns(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> List[Dict[str, Any]]:
    sys.stderr.write(f"MAIN.PY: tool_get_system_patterns received raw_args_from_fastmcp: type={type(raw_args_from_fastmcp)}, value={raw_args_from_fastmcp}\\n"); sys.stderr.flush()
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        if workspace_id_val is None:
            log.error(f"CRITICAL: 'workspace_id' not found for get_system_patterns. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id' in arguments for get_system_patterns")
        pydantic_args = models.GetSystemPatternsArgs(workspace_id=workspace_id_val)
        return mcp_handlers.handle_get_system_patterns(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in get_system_patterns handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for get_system_patterns: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing get_system_patterns: {type(e).__name__}")

@conport_mcp.tool(name="log_custom_data")
async def tool_log_custom_data(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> Dict[str, Any]:
    sys.stderr.write(f"MAIN.PY: tool_log_custom_data received raw_args_from_fastmcp: type={type(raw_args_from_fastmcp)}, value={raw_args_from_fastmcp}\\n"); sys.stderr.flush()
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        category_val = raw_args_from_fastmcp.get("category")
        key_val = raw_args_from_fastmcp.get("key")
        value_val = raw_args_from_fastmcp.get("value") # Pydantic will validate 'Any'
        if workspace_id_val is None or category_val is None or key_val is None or value_val is None: # value is required by model
            log.error(f"CRITICAL: Missing required fields for log_custom_data. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id', 'category', 'key', or 'value' in arguments for log_custom_data")
        pydantic_args = models.LogCustomDataArgs(
            workspace_id=workspace_id_val,
            category=category_val,
            key=key_val,
            value=value_val
        )
        return mcp_handlers.handle_log_custom_data(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in log_custom_data handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for log_custom_data: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing log_custom_data: {type(e).__name__}")

@conport_mcp.tool(name="get_custom_data")
async def tool_get_custom_data(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> List[Dict[str, Any]]:
    sys.stderr.write(f"MAIN.PY: tool_get_custom_data received raw_args_from_fastmcp: type={type(raw_args_from_fastmcp)}, value={raw_args_from_fastmcp}\\n"); sys.stderr.flush()
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        if workspace_id_val is None:
            log.error(f"CRITICAL: 'workspace_id' not found for get_custom_data. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id' in arguments for get_custom_data")
        pydantic_args = models.GetCustomDataArgs(
            workspace_id=workspace_id_val,
            category=raw_args_from_fastmcp.get("category"), # Optional
            key=raw_args_from_fastmcp.get("key") # Optional
        )
        return mcp_handlers.handle_get_custom_data(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in get_custom_data handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for get_custom_data: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing get_custom_data: {type(e).__name__}")

@conport_mcp.tool(name="delete_custom_data")
async def tool_delete_custom_data(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> Dict[str, Any]:
    sys.stderr.write(f"MAIN.PY: tool_delete_custom_data received raw_args_from_fastmcp: type={type(raw_args_from_fastmcp)}, value={raw_args_from_fastmcp}\\n"); sys.stderr.flush()
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        category_val = raw_args_from_fastmcp.get("category")
        key_val = raw_args_from_fastmcp.get("key")
        if workspace_id_val is None or category_val is None or key_val is None:
            log.error(f"CRITICAL: Missing required fields for delete_custom_data. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id', 'category', or 'key' in arguments for delete_custom_data")
        pydantic_args = models.DeleteCustomDataArgs(
            workspace_id=workspace_id_val,
            category=category_val,
            key=key_val
        )
        return mcp_handlers.handle_delete_custom_data(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in delete_custom_data handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for delete_custom_data: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing delete_custom_data: {type(e).__name__}")
@conport_mcp.tool(name="search_project_glossary_fts")
async def tool_search_project_glossary_fts(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> List[Dict[str, Any]]:
    sys.stderr.write(f"MAIN.PY: tool_search_project_glossary_fts received raw_args_from_fastmcp: type={type(raw_args_from_fastmcp)}, value={raw_args_from_fastmcp}\\n"); sys.stderr.flush()
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        query_term_val = raw_args_from_fastmcp.get("query_term")
        if workspace_id_val is None or query_term_val is None:
            log.error(f"CRITICAL: Missing 'workspace_id' or 'query_term' for search_project_glossary_fts. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id' or 'query_term' in arguments for search_project_glossary_fts")
        pydantic_args = models.SearchProjectGlossaryArgs(
            workspace_id=workspace_id_val,
            query_term=query_term_val,
            limit=raw_args_from_fastmcp.get("limit") # Optional
        )
        return mcp_handlers.handle_search_project_glossary_fts(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in search_project_glossary_fts handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for search_project_glossary_fts: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing search_project_glossary_fts: {type(e).__name__}")

@conport_mcp.tool(name="export_conport_to_markdown")
async def tool_export_conport_to_markdown(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> Dict[str, Any]:
    sys.stderr.write(f"MAIN.PY: tool_export_conport_to_markdown received raw_args_from_fastmcp: type={type(raw_args_from_fastmcp)}, value={raw_args_from_fastmcp}\\n"); sys.stderr.flush()
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        if workspace_id_val is None:
            log.error(f"CRITICAL: 'workspace_id' not found for export_conport_to_markdown. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id' in arguments for export_conport_to_markdown")
        pydantic_args = models.ExportConportToMarkdownArgs(
            workspace_id=workspace_id_val,
            output_path=raw_args_from_fastmcp.get("output_path") # Optional
        )
        return mcp_handlers.handle_export_conport_to_markdown(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in export_conport_to_markdown handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for export_conport_to_markdown: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing export_conport_to_markdown: {type(e).__name__}")

@conport_mcp.tool(name="import_markdown_to_conport")
async def tool_import_markdown_to_conport(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> Dict[str, Any]:
    sys.stderr.write(f"MAIN.PY: tool_import_markdown_to_conport received raw_args_from_fastmcp: type={type(raw_args_from_fastmcp)}, value={raw_args_from_fastmcp}\\n"); sys.stderr.flush()
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        if workspace_id_val is None:
            log.error(f"CRITICAL: 'workspace_id' not found for import_markdown_to_conport. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id' in arguments for import_markdown_to_conport")
        pydantic_args = models.ImportMarkdownToConportArgs(
            workspace_id=workspace_id_val,
            input_path=raw_args_from_fastmcp.get("input_path") # Optional
        )
        return mcp_handlers.handle_import_markdown_to_conport(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in import_markdown_to_conport handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for import_markdown_to_conport: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing import_markdown_to_conport: {type(e).__name__}")

# Mount the FastMCP SSE app to the FastAPI app at the /mcp path
# This will handle GET for SSE and POST for JSON-RPC client requests
app.mount("/mcp", conport_mcp.sse_app())
log.info("Mounted FastMCP app at /mcp")

# Keep a simple root endpoint for health checks or basic info
@app.get("/")
async def read_root():
    return {"message": "ConPort MCP Server is running. MCP endpoint at /mcp"}

# STDIO mode execution (if needed directly, though FastMCP might have its own way)
# For now, we'll keep our stdio_run function but it won't be the primary way if using FastMCP for HTTP.
# FastMCP's `mcp.run()` or `mcp dev` might be the new way for stdio.
# The `pyproject.toml` script points to `cli_entry_point` which will run uvicorn for HTTP.
# If stdio is still desired as a direct execution mode for the *packaged* tool,
# `main_logic` would need to be adapted to call something like `conport_mcp.run(transport="stdio")`
# instead of uvicorn.

# For now, the focus is HTTP via FastMCP mounting.
# The old stdio_mode and manual JSON-RPC message handling can be removed.

# Old manual JSON-RPC handling, SSE, and stdio mode can be removed or significantly refactored
# if FastMCP handles these transports. For now, focusing on HTTP mode via FastMCP.
# The run_stdio_mode() might be replaced by conport_mcp.run(transport="stdio") if needed.
sys.stderr.write(f"MAIN.PY: Value of __name__ is: '{__name__}'\\n"); sys.stderr.flush() # Simplified prefix

def main_logic(sys_args=None):
    """
    Configures and runs the ConPort server (HTTP mode via Uvicorn).
    The actual MCP logic is handled by the FastMCP instance mounted on the FastAPI app.
    """
    parser = argparse.ArgumentParser(description="ConPort MCP Server (FastMCP/HTTP)")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind the HTTP server to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the HTTP server to (default: 8000)"
    )
    # --workspace_id is not directly used by uvicorn.run for the app itself,
    # but it's good for the CLI to accept it for consistency if an IDE launches it.
    # The actual workspace_id is handled per-request by FastMCP tools.
    parser.add_argument(
        "--workspace_id",
        type=str,
        required=False, # No longer strictly required for server startup itself
        help="Optional: Default workspace ID (primarily for IDE launch context, tool calls still need it)."
    )
    # The --mode argument might be deprecated if FastMCP only runs HTTP this way,
    # or we add a condition here to call conport_mcp.run(transport="stdio")
    parser.add_argument(
        "--mode",
        choices=["http", "stdio"], # Add http, stdio might be handled by FastMCP directly
        default="http",
        help="Server communication mode (default: http for FastMCP mounted app)"
    )

    args = parser.parse_args(args=sys_args)
    log.info(f"Parsed CLI args: {args}")

    if args.mode == "http":
        log.info(f"Starting ConPort HTTP server (via FastMCP) on {args.host}:{args.port}")
        # The FastAPI `app` (with FastMCP mounted) is run by Uvicorn
        uvicorn.run(app, host=args.host, port=args.port)
    elif args.mode == "stdio":
        log.info(f"Starting ConPort in STDIO mode using FastMCP for initial CLI arg workspace_id: {args.workspace_id}")
        sys.stderr.write("MAIN.PY: Entered STDIO mode block.\\n"); sys.stderr.flush()
        
        effective_workspace_id = args.workspace_id
        if args.workspace_id == "${workspaceFolder}":
            import os
            current_cwd = os.getcwd()
            warning_msg = (
                f"MAIN.PY: WARNING - Workspace ID was literally '${{workspaceFolder}}'. "
                f"This variable was not expanded by the client IDE. "
                f"Falling back to current working directory as workspace_id: {current_cwd}. "
                f"Ensure CWD in MCP config ('{current_cwd}') is the correct project workspace."
            )
            log.warning(warning_msg)
            sys.stderr.write(warning_msg + "\\n"); sys.stderr.flush()
            effective_workspace_id = current_cwd
        
        sys.stderr.write(f"MAIN.PY: STDIO mode - Effective workspace_id for DB validation: {effective_workspace_id}\\n"); sys.stderr.flush()
        sys.stderr.write("MAIN.PY: STDIO mode - Before DB path validation.\\n"); sys.stderr.flush()
        try:
            from src.context_portal_mcp.core.config import get_database_path # Ensure it's imported
            get_database_path(effective_workspace_id) # Validate path early
            log.info(f"Workspace ID {effective_workspace_id} path validated for DB for STDIO mode.")
            sys.stderr.write("MAIN.PY: STDIO mode - DB path validated successfully.\\n"); sys.stderr.flush()
        except Exception as e:
            log.error(f"Invalid effective_workspace_id '{effective_workspace_id}' for database in STDIO mode: {e}")
            sys.stderr.write(f"MAIN.PY: STDIO mode - DB path validation FAILED for '{effective_workspace_id}': {e}\\n"); sys.stderr.flush()
            sys.exit(1)
        
        # Note: The `FastMCP.run()` method is synchronous and will block until the server stops.
        # It requires the `mcp[cli]` extra to be installed for `mcp.server.stdio.run_server_stdio`.
        sys.stderr.write("MAIN.PY: STDIO mode - Before conport_mcp.run(transport='stdio').\\n"); sys.stderr.flush()
        try:
            # The `settings` attribute on FastMCP can be used to pass runtime config.
            # However, `workspace_id` is not a standard FastMCP setting for `run()`.
            # It's expected to be part of the tool call parameters.
            # The primary role of --workspace_id for stdio here is for the IDE's launch config.
            conport_mcp.run(transport="stdio")
            sys.stderr.write("MAIN.PY: STDIO mode - conport_mcp.run(transport='stdio') EXITED WITHOUT ERROR (UNEXPECTED if blocking).\\n"); sys.stderr.flush()
        except Exception as e:
            log.exception("Error running FastMCP in STDIO mode")
            sys.stderr.write(f"MAIN.PY: STDIO mode - conport_mcp.run(transport='stdio') FAILED: {e}\\n"); sys.stderr.flush()
            sys.exit(1)

    else:
        log.error(f"Unsupported mode: {args.mode}")
        sys.exit(1)

def cli_entry_point():
    """Entry point for the 'conport-server' command-line script."""
    log.info("ConPort MCP Server CLI entry point called.")
    main_logic()

if __name__ == "__main__":
    cli_entry_point()
# else: No specific action needed if imported, FastMCP instance is available.
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