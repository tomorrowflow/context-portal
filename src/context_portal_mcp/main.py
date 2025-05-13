import sys
import uvicorn
from fastapi import FastAPI
import logging
import argparse
import os
from typing import Dict, Any, Optional, AsyncIterator, List # Added AsyncIterator and List
from contextlib import asynccontextmanager # Added

# MCP SDK imports
from mcp.server.fastmcp import FastMCP, Context as MCPContext # Renamed Context to avoid clash

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
    lifespan=conport_lifespan
)

# --- FastAPI App ---
# The FastAPI app will be the main ASGI app, and FastMCP will be mounted onto it.
# We keep our own FastAPI app instance in case we want to add other non-MCP HTTP endpoints later.
app = FastAPI(title="ConPort MCP Server Wrapper", version=CONPORT_VERSION)

# --- Adapt and Register Tools with FastMCP ---
# We use our Pydantic models as input_schema for robust validation.

@conport_mcp.tool(name="get_product_context")
async def tool_get_product_context(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> Dict[str, Any]:
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
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        content_val = raw_args_from_fastmcp.get("content") # This can now be None
        patch_content_val = raw_args_from_fastmcp.get("patch_content") # New optional field

        if workspace_id_val is None:
            log.error(f"CRITICAL: Missing 'workspace_id' in raw_args_from_fastmcp for update_product_context. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id' in arguments for update_product_context")
        
        # Pydantic model UpdateContextArgs will validate that either content or patch_content is provided
        pydantic_args = models.UpdateContextArgs(
            workspace_id=workspace_id_val,
            content=content_val,
            patch_content=patch_content_val
        )
        return mcp_handlers.handle_update_product_context(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in update_product_context handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for update_product_context: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing update_product_context: {type(e).__name__}")

@conport_mcp.tool(name="get_active_context")
async def tool_get_active_context(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> Dict[str, Any]:
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
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        content_val = raw_args_from_fastmcp.get("content") # This can now be None
        patch_content_val = raw_args_from_fastmcp.get("patch_content") # New optional field

        if workspace_id_val is None:
            log.error(f"CRITICAL: Missing 'workspace_id' in raw_args_from_fastmcp for update_active_context. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id' in arguments for update_active_context")

        # Pydantic model UpdateContextArgs will validate that either content or patch_content is provided
        pydantic_args = models.UpdateContextArgs(
            workspace_id=workspace_id_val,
            content=content_val,
            patch_content=patch_content_val
        )
        return mcp_handlers.handle_update_active_context(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in update_active_context handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for update_active_context: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing update_active_context: {type(e).__name__}")

@conport_mcp.tool(name="log_decision")
async def tool_log_decision(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> Dict[str, Any]:
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
            implementation_details=raw_args_from_fastmcp.get("implementation_details"), # Optional
            tags=raw_args_from_fastmcp.get("tags") # Optional
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
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        if workspace_id_val is None:
            log.error(f"CRITICAL: 'workspace_id' not found for get_decisions. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id' in arguments for get_decisions")
        pydantic_args = models.GetDecisionsArgs(
            workspace_id=workspace_id_val,
            limit=raw_args_from_fastmcp.get("limit"), # Optional
            tags_filter_include_all=raw_args_from_fastmcp.get("tags_filter_include_all"), # Optional
            tags_filter_include_any=raw_args_from_fastmcp.get("tags_filter_include_any")  # Optional
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
            parent_id=raw_args_from_fastmcp.get("parent_id"), # Optional
            linked_item_type=raw_args_from_fastmcp.get("linked_item_type"), # Optional
            linked_item_id=raw_args_from_fastmcp.get("linked_item_id"), # Optional
            link_relationship_type=raw_args_from_fastmcp.get("link_relationship_type", "relates_to_progress") # Optional with default
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

@conport_mcp.tool(name="update_progress")
async def tool_update_progress(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> Dict[str, Any]:
    """
    MCP tool wrapper for update_progress.
    Validates arguments and calls the handler.
    """
    try:
        # Pydantic model will parse and validate the raw dictionary.
        log.debug(f"update_progress raw_args: {raw_args_from_fastmcp}")
        pydantic_args = models.UpdateProgressArgs(**raw_args_from_fastmcp)
        return mcp_handlers.handle_update_progress(pydantic_args)
    except exceptions.ToolArgumentError as e:
        log.error(f"Argument validation error for update_progress: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Invalid arguments for update_progress: {e}")
    except exceptions.ContextPortalError as e:
        log.error(f"Error in update_progress handler: {e}")
        raise
    except Exception as e:
        log.error(f"Unexpected error processing args for update_progress: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing update_progress: {type(e).__name__} - {e}")

@conport_mcp.tool(name="delete_progress_by_id")
async def tool_delete_progress_by_id(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> Dict[str, Any]:
    """
    MCP tool wrapper for delete_progress_by_id.
    Validates arguments and calls the handler.
    """
    try:
        # Pydantic model will parse and validate the raw dictionary.
        log.debug(f"delete_progress_by_id raw_args: {raw_args_from_fastmcp}")
        pydantic_args = models.DeleteProgressByIdArgs(**raw_args_from_fastmcp)
        return mcp_handlers.handle_delete_progress_by_id(pydantic_args)
    except exceptions.ToolArgumentError as e:
        log.error(f"Argument validation error for delete_progress_by_id: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Invalid arguments for delete_progress_by_id: {e}")
    except exceptions.ContextPortalError as e:
        log.error(f"Error in delete_progress_by_id handler: {e}")
        raise
    except Exception as e:
        log.error(f"Unexpected error processing args for delete_progress_by_id: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing delete_progress_by_id: {type(e).__name__} - {e}")

@conport_mcp.tool(name="log_system_pattern")
async def tool_log_system_pattern(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> Dict[str, Any]:
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        name_val = raw_args_from_fastmcp.get("name")
        if workspace_id_val is None or name_val is None:
            log.error(f"CRITICAL: Missing 'workspace_id' or 'name' for log_system_pattern. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id' or 'name' in arguments for log_system_pattern")
        pydantic_args = models.LogSystemPatternArgs(
            workspace_id=workspace_id_val,
            name=name_val,
            description=raw_args_from_fastmcp.get("description"), # Optional
            tags=raw_args_from_fastmcp.get("tags") # Optional
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
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        if workspace_id_val is None:
            log.error(f"CRITICAL: 'workspace_id' not found for get_system_patterns. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id' in arguments for get_system_patterns")
        pydantic_args = models.GetSystemPatternsArgs(
            workspace_id=workspace_id_val,
            tags_filter_include_all=raw_args_from_fastmcp.get("tags_filter_include_all"), # Optional
            tags_filter_include_any=raw_args_from_fastmcp.get("tags_filter_include_any")  # Optional
        )
        return mcp_handlers.handle_get_system_patterns(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in get_system_patterns handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for get_system_patterns: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing get_system_patterns: {type(e).__name__}")

@conport_mcp.tool(name="log_custom_data")
async def tool_log_custom_data(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> Dict[str, Any]:
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

@conport_mcp.tool(name="link_conport_items")
async def tool_link_conport_items(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> Dict[str, Any]:
    try:
        # Extract all fields for LinkConportItemsArgs
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        source_item_type_val = raw_args_from_fastmcp.get("source_item_type")
        source_item_id_val = raw_args_from_fastmcp.get("source_item_id")
        target_item_type_val = raw_args_from_fastmcp.get("target_item_type")
        target_item_id_val = raw_args_from_fastmcp.get("target_item_id")
        relationship_type_val = raw_args_from_fastmcp.get("relationship_type")

        if not all([workspace_id_val, source_item_type_val, source_item_id_val,
                    target_item_type_val, target_item_id_val, relationship_type_val]):
            log.error(f"CRITICAL: Missing required fields for link_conport_items. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing required fields in arguments for link_conport_items")

        pydantic_args = models.LinkConportItemsArgs(
            workspace_id=workspace_id_val,
            source_item_type=source_item_type_val,
            source_item_id=str(source_item_id_val), # Ensure string
            target_item_type=target_item_type_val,
            target_item_id=str(target_item_id_val), # Ensure string
            relationship_type=relationship_type_val,
            description=raw_args_from_fastmcp.get("description") # Optional
        )
        return mcp_handlers.handle_link_conport_items(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in link_conport_items handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for link_conport_items: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing link_conport_items: {type(e).__name__}")

@conport_mcp.tool(name="get_linked_items")
async def tool_get_linked_items(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> List[Dict[str, Any]]:
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        item_type_val = raw_args_from_fastmcp.get("item_type")
        item_id_val = raw_args_from_fastmcp.get("item_id")

        if not all([workspace_id_val, item_type_val, item_id_val]):
            log.error(f"CRITICAL: Missing required fields for get_linked_items. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id', 'item_type', or 'item_id' in arguments for get_linked_items")

        pydantic_args = models.GetLinkedItemsArgs(
            workspace_id=workspace_id_val,
            item_type=item_type_val,
            item_id=str(item_id_val), # Ensure string
            relationship_type_filter=raw_args_from_fastmcp.get("relationship_type_filter"), # Optional
            linked_item_type_filter=raw_args_from_fastmcp.get("linked_item_type_filter"), # Optional
            limit=raw_args_from_fastmcp.get("limit") # Optional
        )
        return mcp_handlers.handle_get_linked_items(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in get_linked_items handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for get_linked_items: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing get_linked_items: {type(e).__name__}")

@conport_mcp.tool(name="search_custom_data_value_fts")
async def tool_search_custom_data_value_fts(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> List[Dict[str, Any]]:
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        query_term_val = raw_args_from_fastmcp.get("query_term")

        if not all([workspace_id_val, query_term_val]):
            log.error(f"CRITICAL: Missing required fields for search_custom_data_value_fts. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id' or 'query_term' in arguments for search_custom_data_value_fts")

        pydantic_args = models.SearchCustomDataValueArgs( # Ensure this model exists and is correct
            workspace_id=workspace_id_val,
            query_term=query_term_val,
            category_filter=raw_args_from_fastmcp.get("category_filter"), # Optional
            limit=raw_args_from_fastmcp.get("limit") # Optional
        )
        return mcp_handlers.handle_search_custom_data_value_fts(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in search_custom_data_value_fts handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for search_custom_data_value_fts: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing search_custom_data_value_fts: {type(e).__name__}")

@conport_mcp.tool(name="batch_log_items")
async def tool_batch_log_items(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> Dict[str, Any]:
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        item_type_val = raw_args_from_fastmcp.get("item_type")
        items_val = raw_args_from_fastmcp.get("items")

        if not all([workspace_id_val, item_type_val, isinstance(items_val, list)]):
            log.error(f"CRITICAL: Missing required fields or incorrect type for 'items' in batch_log_items. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id', 'item_type', or 'items' (must be a list) in arguments for batch_log_items")

        pydantic_args = models.BatchLogItemsArgs(
            workspace_id=workspace_id_val,
            item_type=item_type_val,
            items=items_val
        )
        return mcp_handlers.handle_batch_log_items(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in batch_log_items handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for batch_log_items: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing batch_log_items: {type(e).__name__}")

@conport_mcp.tool(name="get_item_history")
async def tool_get_item_history(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> List[Dict[str, Any]]:
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        item_type_val = raw_args_from_fastmcp.get("item_type")

        if not all([workspace_id_val, item_type_val]):
            log.error(f"CRITICAL: Missing required fields for get_item_history. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id' or 'item_type' in arguments for get_item_history")

        pydantic_args = models.GetItemHistoryArgs(
            workspace_id=workspace_id_val,
            item_type=item_type_val,
            limit=raw_args_from_fastmcp.get("limit"),
            before_timestamp=raw_args_from_fastmcp.get("before_timestamp"),
            after_timestamp=raw_args_from_fastmcp.get("after_timestamp"),
            version=raw_args_from_fastmcp.get("version")
        )
        return mcp_handlers.handle_get_item_history(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in get_item_history handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for get_item_history: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing get_item_history: {type(e).__name__}")

@conport_mcp.tool(name="delete_decision_by_id")
async def tool_delete_decision_by_id(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> Dict[str, Any]:
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        decision_id_val = raw_args_from_fastmcp.get("decision_id")
        if not all([workspace_id_val, decision_id_val]):
            raise ValueError("Missing 'workspace_id' or 'decision_id'")
        pydantic_args = models.DeleteDecisionByIdArgs(workspace_id=workspace_id_val, decision_id=decision_id_val)
        return mcp_handlers.handle_delete_decision_by_id(pydantic_args)
    except Exception as e:
        log.error(f"Error processing args for delete_decision_by_id: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing delete_decision_by_id: {type(e).__name__}")

@conport_mcp.tool(name="delete_system_pattern_by_id")
async def tool_delete_system_pattern_by_id(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> Dict[str, Any]:
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        pattern_id_val = raw_args_from_fastmcp.get("pattern_id")
        if not all([workspace_id_val, pattern_id_val]):
            raise ValueError("Missing 'workspace_id' or 'pattern_id'")
        pydantic_args = models.DeleteSystemPatternByIdArgs(workspace_id=workspace_id_val, pattern_id=pattern_id_val)
        return mcp_handlers.handle_delete_system_pattern_by_id(pydantic_args)
    except Exception as e:
        log.error(f"Error processing args for delete_system_pattern_by_id: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing delete_system_pattern_by_id: {type(e).__name__}")

@conport_mcp.tool(name="get_conport_schema")
async def tool_get_conport_schema(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> Dict[str, Dict[str, Any]]:
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        if workspace_id_val is None:
            log.error(f"CRITICAL: 'workspace_id' not found in raw_args_from_fastmcp for get_conport_schema. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id' in arguments for get_conport_schema")
        pydantic_args = models.GetConportSchemaArgs(workspace_id=workspace_id_val) # Corrected model name
        return mcp_handlers.handle_get_conport_schema(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in get_conport_schema handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for get_conport_schema: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing get_conport_schema: {type(e).__name__}")

@conport_mcp.tool(name="get_recent_activity_summary")
async def tool_get_recent_activity_summary(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> Dict[str, Any]:
    try:
        workspace_id_val = raw_args_from_fastmcp.get("workspace_id")
        if workspace_id_val is None:
            log.error(f"CRITICAL: 'workspace_id' not found for get_recent_activity_summary. Received: {raw_args_from_fastmcp}")
            raise ValueError("Missing 'workspace_id' in arguments for get_recent_activity_summary")
        
        # Pydantic will handle type conversion for datetime if 'since_timestamp' is an ISO string
        pydantic_args = models.GetRecentActivitySummaryArgs(
            workspace_id=workspace_id_val,
            hours_ago=raw_args_from_fastmcp.get("hours_ago"),
            since_timestamp=raw_args_from_fastmcp.get("since_timestamp"),
            limit_per_type=raw_args_from_fastmcp.get("limit_per_type")
        )
        return mcp_handlers.handle_get_recent_activity_summary(pydantic_args)
    except exceptions.ContextPortalError as e:
        log.error(f"Error in get_recent_activity_summary handler: {e}")
        raise
    except Exception as e:
        log.error(f"Error processing args for get_recent_activity_summary: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing get_recent_activity_summary: {type(e).__name__}")

@conport_mcp.tool(name="semantic_search_conport")
async def tool_semantic_search_conport(raw_args_from_fastmcp: Dict[str, Any], ctx: MCPContext) -> List[Dict[str, Any]]:
    """
    MCP tool wrapper for semantic_search_conport.
    It validates arguments using SemanticSearchConportArgs Pydantic model and calls the handler.
    """
    try:
        # Pydantic model will parse and validate the raw dictionary.
        # FastMCP typically passes the raw dict as the first arg.
        log.debug(f"semantic_search_conport raw_args: {raw_args_from_fastmcp}")
        pydantic_args = models.SemanticSearchConportArgs(**raw_args_from_fastmcp)
        # The handler should be async to be awaited here.
        # If mcp_handlers.handle_semantic_search_conport is not async,
        # it would need to be run in a thread pool executor for a truly async app.
        # For now, assuming it will be made async or FastMCP handles sync handlers appropriately.
        return await mcp_handlers.handle_semantic_search_conport(pydantic_args)
    except exceptions.ToolArgumentError as e: # Catch validation errors from Pydantic model itself
        log.error(f"Argument validation error for semantic_search_conport: {e}. Received raw: {raw_args_from_fastmcp}")
        # Re-raise as ContextPortalError or let FastMCP handle it if it maps ValidationError
        raise exceptions.ContextPortalError(f"Invalid arguments for semantic_search_conport: {e}")
    except exceptions.ContextPortalError as e:
        log.error(f"Error in semantic_search_conport handler: {e}")
        raise
    except Exception as e:
        log.error(f"Unexpected error processing args for semantic_search_conport: {e}. Received raw: {raw_args_from_fastmcp}")
        raise exceptions.ContextPortalError(f"Server error processing semantic_search_conport: {type(e).__name__} - {e}")

# Mount the FastMCP SSE app to the FastAPI app at the /mcp path
# This will handle GET for SSE and POST for JSON-RPC client requests
app.mount("/mcp", conport_mcp.sse_app())
log.info("Mounted FastMCP app at /mcp")

# Keep a simple root endpoint for health checks or basic info
@app.get("/")
async def read_root():
    return {"message": "ConPort MCP Server is running. MCP endpoint at /mcp"}


# Determine the absolute path to the root of the ConPort server project
# Assumes this script (main.py) is at src/context_portal_mcp/main.py
CONPORT_SERVER_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
log.info(f"ConPort Server Root Directory identified as: {CONPORT_SERVER_ROOT_DIR}")
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
        
        effective_workspace_id = args.workspace_id
        if args.workspace_id == "${workspaceFolder}":
            # import os # Moved to top-level imports
            current_cwd = os.getcwd()
            warning_msg = (
                f"MAIN.PY: WARNING - Workspace ID was literally '${{workspaceFolder}}'. "
                f"This variable was not expanded by the client IDE. "
                f"Falling back to current working directory as workspace_id: {current_cwd}. "
                f"Ensure CWD in MCP config ('{current_cwd}') is the correct project workspace."
            )
            log.warning(warning_msg)
            effective_workspace_id = current_cwd
        
            # CRITICAL CHECK: Prevent creating DB in server's own directory due to misconfiguration
            if effective_workspace_id and os.path.abspath(effective_workspace_id) == CONPORT_SERVER_ROOT_DIR:
                error_msg = (
                    f"CRITICAL ERROR: STDIO mode effective_workspace_id ('{effective_workspace_id}') "
                    f"resolved to the ConPort server's own root directory ('{CONPORT_SERVER_ROOT_DIR}'). "
                    "This is likely due to a client-side MCP configuration error where "
                    "'--workspace_id' was not correctly resolved to your target project path, "
                    "and no 'cwd' was set to the target project by the client. "
                    "ConPort will NOT create a database within its own installation directory. "
                    "Please correct your MCP client configuration to provide an absolute path "
                    "for '--workspace_id' or ensure your client sets 'cwd' to your target project."
                )
                log.critical(error_msg)
                sys.exit(1)
        
        try:
            # from src.context_portal_mcp.core.config import get_database_path # Import happens at module level
            # get_database_path(effective_workspace_id) # EARLY VALIDATION REMOVED - Path validation and dir creation will occur on first DB access.
            
            if not effective_workspace_id or not os.path.isdir(effective_workspace_id): # Basic check if path is a directory
                 log.error(f"STDIO mode: effective_workspace_id ('{effective_workspace_id}') is not a valid directory. Please ensure client provides a correct absolute path or sets 'cwd' appropriately if using '${{workspaceFolder}}'.")
                 sys.exit(1)

            log.info(f"STDIO mode: Using effective_workspace_id '{effective_workspace_id}'. Database directory will be created on first actual DB use.")
        except Exception as e: # Catch any other unexpected errors during this initial workspace_id handling
            log.error(f"Unexpected error processing effective_workspace_id '{effective_workspace_id}' in STDIO mode setup: {e}")
            sys.exit(1)
        
        # Note: The `FastMCP.run()` method is synchronous and will block until the server stops.
        # It requires the `mcp[cli]` extra to be installed for `mcp.server.stdio.run_server_stdio`.
        try:
            # The `settings` attribute on FastMCP can be used to pass runtime config.
            # However, `workspace_id` is not a standard FastMCP setting for `run()`.
            # It's expected to be part of the tool call parameters.
            # The primary role of --workspace_id for stdio here is for the IDE's launch config.
            conport_mcp.run(transport="stdio")
        except Exception as e:
            log.exception("Error running FastMCP in STDIO mode")
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
 