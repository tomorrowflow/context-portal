"""Functions implementing the logic for each MCP tool."""

from typing import Dict, Any, List, Optional

from pydantic import ValidationError

from ..db import database as db
from ..db import models
from ..core.exceptions import ToolArgumentError, DatabaseError, ContextPortalError

# --- Tool Handler Functions ---

def handle_get_product_context(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handles the 'get_product_context' MCP tool."""
    try:
        args_model = models.GetContextArgs(**arguments)
    except ValidationError as e:
        raise ToolArgumentError(f"Invalid arguments for get_product_context: {e}")

    try:
        context_model = db.get_product_context(args_model.workspace_id)
        # Return the content dictionary directly
        return context_model.content
    except DatabaseError as e:
        # Re-raise or handle specific DB errors if needed
        raise ContextPortalError(f"Database error getting product context: {e}")
    except Exception as e:
        raise ContextPortalError(f"Unexpected error in get_product_context: {e}")


def handle_update_product_context(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handles the 'update_product_context' MCP tool."""
    try:
        args_model = models.UpdateContextArgs(**arguments)
    except ValidationError as e:
        raise ToolArgumentError(f"Invalid arguments for update_product_context: {e}")

    try:
        # Validate/create the model instance before updating
        # Create the DB model instance from validated args
        context_model = models.ProductContext(content=args_model.content)
        db.update_product_context(args_model.workspace_id, context_model)
        return {"status": "success", "message": "Product context updated."}
    except ValidationError as e:
         raise ToolArgumentError(f"Invalid content structure: {e}")
    except DatabaseError as e:
        raise ContextPortalError(f"Database error updating product context: {e}")
    except Exception as e:
        raise ContextPortalError(f"Unexpected error in update_product_context: {e}")


def handle_log_decision(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handles the 'log_decision' MCP tool."""
    try:
        # Use Pydantic model for validation
        args_model = models.LogDecisionArgs(**arguments)
        decision_to_log = models.Decision(
            summary=args_model.summary,
            rationale=args_model.rationale,
            implementation_details=args_model.implementation_details
            # Timestamp is added automatically by the model
        )
        logged_decision = db.log_decision(args_model.workspace_id, decision_to_log)
        # Return the logged decision as a dictionary
        return logged_decision.model_dump(mode='json') # Use model_dump for Pydantic v2+
    except ValidationError as e:
        raise ToolArgumentError(f"Invalid arguments for log_decision: {e}")
    except DatabaseError as e:
        raise ContextPortalError(f"Database error logging decision: {e}")
    except Exception as e:
        raise ContextPortalError(f"Unexpected error in log_decision: {e}")

# --- Added handlers ---

def handle_get_decisions(arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Handles the 'get_decisions' MCP tool."""
    try:
        args_model = models.GetDecisionsArgs(**arguments)
    except ValidationError as e:
        raise ToolArgumentError(f"Invalid arguments for get_decisions: {e}")

    try:
        # Access validated arguments
        decisions_list = db.get_decisions(args_model.workspace_id, limit=args_model.limit)
        # Convert list of models to list of dicts
        return [d.model_dump(mode='json') for d in decisions_list]
    # ValueError is handled by Pydantic validation now
    except DatabaseError as e:
        raise ContextPortalError(f"Database error getting decisions: {e}")
    except Exception as e:
        raise ContextPortalError(f"Unexpected error in get_decisions: {e}")

def handle_get_active_context(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handles the 'get_active_context' MCP tool."""
    try:
        args_model = models.GetContextArgs(**arguments)
    except ValidationError as e:
        raise ToolArgumentError(f"Invalid arguments for get_active_context: {e}")
    try:
        context_model = db.get_active_context(args_model.workspace_id)
        return context_model.content
    except DatabaseError as e:
        raise ContextPortalError(f"Database error getting active context: {e}")
    except Exception as e:
        raise ContextPortalError(f"Unexpected error in get_active_context: {e}")

def handle_update_active_context(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handles the 'update_active_context' MCP tool."""
    try:
        args_model = models.UpdateContextArgs(**arguments)
    except ValidationError as e:
        raise ToolArgumentError(f"Invalid arguments for update_active_context: {e}")
    try:
        context_model = models.ActiveContext(content=args_model.content)
        db.update_active_context(args_model.workspace_id, context_model)
        return {"status": "success", "message": "Active context updated."}
    except ValidationError as e:
         raise ToolArgumentError(f"Invalid content structure: {e}")
    except DatabaseError as e:
        raise ContextPortalError(f"Database error updating active context: {e}")
    except Exception as e:
        raise ContextPortalError(f"Unexpected error in update_active_context: {e}")

def handle_log_progress(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handles the 'log_progress' MCP tool."""
    try:
        args_model = models.LogProgressArgs(**arguments)
    except ValidationError as e:
        raise ToolArgumentError(f"Invalid arguments for log_progress: {e}")

    try:

        progress_to_log = models.ProgressEntry(
            status=args_model.status,
            description=args_model.description,
            parent_id=args_model.parent_id # Pydantic handles Optional[int]
        )
        logged_progress = db.log_progress(args_model.workspace_id, progress_to_log)
        return logged_progress.model_dump(mode='json')
    except ValidationError as e: # ValueError handled by Pydantic
        raise ToolArgumentError(f"Invalid arguments for log_progress: {e}")
    except DatabaseError as e:
        raise ContextPortalError(f"Database error logging progress: {e}")
    except Exception as e:
        raise ContextPortalError(f"Unexpected error in log_progress: {e}")

def handle_get_progress(arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Handles the 'get_progress' MCP tool."""
    try:
        args_model = models.GetProgressArgs(**arguments)
    except ValidationError as e:
        raise ToolArgumentError(f"Invalid arguments for get_progress: {e}")

    try:
        # Access validated arguments
        progress_list = db.get_progress(
            args_model.workspace_id,
            status_filter=args_model.status_filter,
            parent_id_filter=args_model.parent_id_filter, # Pydantic handles Optional[int]
            limit=args_model.limit
        )
        return [p.model_dump(mode='json') for p in progress_list]
    # ValueError handled by Pydantic
    except DatabaseError as e:
        raise ContextPortalError(f"Database error getting progress: {e}")
    except Exception as e:
        raise ContextPortalError(f"Unexpected error in get_progress: {e}")

def handle_log_system_pattern(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handles the 'log_system_pattern' MCP tool."""
    try:
        args_model = models.LogSystemPatternArgs(**arguments)
    except ValidationError as e:
        raise ToolArgumentError(f"Invalid arguments for log_system_pattern: {e}")
    try:
        pattern_to_log = models.SystemPattern(name=args_model.name, description=args_model.description)
        logged_pattern = db.log_system_pattern(args_model.workspace_id, pattern_to_log)
        return logged_pattern.model_dump(mode='json')
    except ValidationError as e:
        raise ToolArgumentError(f"Invalid arguments for log_system_pattern: {e}")
    except DatabaseError as e:
        raise ContextPortalError(f"Database error logging system pattern: {e}")
    except Exception as e:
        raise ContextPortalError(f"Unexpected error in log_system_pattern: {e}")

def handle_get_system_patterns(arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Handles the 'get_system_patterns' MCP tool."""
    try:
        args_model = models.GetSystemPatternsArgs(**arguments)
    except ValidationError as e:
        raise ToolArgumentError(f"Invalid arguments for get_system_patterns: {e}")
    try:
        patterns_list = db.get_system_patterns(args_model.workspace_id)
        return [p.model_dump(mode='json') for p in patterns_list]
    except DatabaseError as e:
        raise ContextPortalError(f"Database error getting system patterns: {e}")
    except Exception as e:
        raise ContextPortalError(f"Unexpected error in get_system_patterns: {e}")

def handle_log_custom_data(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handles the 'log_custom_data' MCP tool."""
    try:
        # Pydantic model handles validation including 'value'
        args_model = models.LogCustomDataArgs(**arguments)
    except ValidationError as e:
        raise ToolArgumentError(f"Invalid arguments for log_custom_data: {e}")
    try:
        # Pydantic model handles JSON validation/parsing for 'value'
        # Create DB model instance from validated args
        data_to_log = models.CustomData(category=args_model.category, key=args_model.key, value=args_model.value)
        logged_data = db.log_custom_data(args_model.workspace_id, data_to_log)
        # Return the logged data, value will be automatically serialized by model_dump
        return logged_data.model_dump(mode='json')
    except ValidationError as e:
        raise ToolArgumentError(f"Invalid arguments for log_custom_data: {e}")
    except DatabaseError as e:
        raise ContextPortalError(f"Database error logging custom data: {e}")
    except Exception as e:
        raise ContextPortalError(f"Unexpected error in log_custom_data: {e}")

def handle_get_custom_data(arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Handles the 'get_custom_data' MCP tool."""
    try:
        args_model = models.GetCustomDataArgs(**arguments)
    except ValidationError as e:
        raise ToolArgumentError(f"Invalid arguments for get_custom_data: {e}")
    try:
        data_list = db.get_custom_data(args_model.workspace_id, category=args_model.category, key=args_model.key)
        # Value is already deserialized by DB function, model_dump handles response serialization
        return [d.model_dump(mode='json') for d in data_list]
    except ValueError as e: # From db function if key w/o category
         raise ToolArgumentError(str(e))
    except DatabaseError as e:
        raise ContextPortalError(f"Database error getting custom data: {e}")
    except Exception as e:
        raise ContextPortalError(f"Unexpected error in get_custom_data: {e}")

def handle_delete_custom_data(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handles the 'delete_custom_data' MCP tool."""
    try:
        args_model = models.DeleteCustomDataArgs(**arguments)
    except ValidationError as e:
        raise ToolArgumentError(f"Invalid arguments for delete_custom_data: {e}")
    try:
        deleted = db.delete_custom_data(args_model.workspace_id, category=args_model.category, key=args_model.key)
        if deleted:
            return {"status": "success", "message": f"Custom data '{category}/{key}' deleted."}
        else:
            # Use a different error type or message? For now, treat as success but indicate not found.
            return {"status": "success", "message": f"Custom data '{category}/{key}' not found."}
    except DatabaseError as e:
        raise ContextPortalError(f"Database error deleting custom data: {e}")
    except Exception as e:
        raise ContextPortalError(f"Unexpected error in delete_custom_data: {e}")

# --- Tool Dispatcher ---

# A dictionary mapping tool names to their handler functions
TOOL_HANDLERS = {
    "get_product_context": handle_get_product_context,
    "update_product_context": handle_update_product_context,
    "get_active_context": handle_get_active_context,
    "update_active_context": handle_update_active_context,
    "log_decision": handle_log_decision,
    "get_decisions": handle_get_decisions,
    "log_progress": handle_log_progress,
    "get_progress": handle_get_progress,
    "log_system_pattern": handle_log_system_pattern,
    "get_system_patterns": handle_get_system_patterns,
    "log_custom_data": handle_log_custom_data,
    "get_custom_data": handle_get_custom_data,
    "delete_custom_data": handle_delete_custom_data,
    # Add other tool names and handlers here if any more are defined
}

def dispatch_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dispatches an MCP tool call to the appropriate handler.

    Args:
        tool_name: The name of the MCP tool to execute.
        arguments: A dictionary containing the arguments for the tool.

    Returns:
        A dictionary representing the result of the tool execution.

    Raises:
        NotImplementedError: If the tool_name is not recognized.
        ContextPortalError: If an error occurs during tool execution.
    """
    if tool_name in TOOL_HANDLERS:
        handler = TOOL_HANDLERS[tool_name]
        try:
            # Ensure workspace_id is present before calling handler (common requirement)
            # workspace_id validation is now handled within each handler via Pydantic models
            return handler(arguments)
        except (ToolArgumentError, DatabaseError, ContextPortalError) as e:
            # Re-raise specific errors
            raise e
        except Exception as e:
            # Catch unexpected errors during handler execution
            raise ContextPortalError(f"Unexpected error executing tool '{tool_name}': {e}")
    else:
        raise NotImplementedError(f"MCP tool '{tool_name}' is not implemented.")