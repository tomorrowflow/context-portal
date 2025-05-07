"""Pydantic models for data validation and structure, mirroring the database schema."""

from pydantic import BaseModel, Field, Json
from typing import Optional, Dict, Any, List
from datetime import datetime

# --- Base Models ---

class BaseContextModel(BaseModel):
    """Base model for single-row context tables."""
    id: int = 1 # Assuming single row with ID 1
    content: Dict[str, Any] # Store actual data as a dictionary

# --- Table Models ---

class ProductContext(BaseContextModel):
    """Model for the product_context table."""
    pass # Inherits structure from BaseContextModel

class ActiveContext(BaseContextModel):
    """Model for the active_context table."""
    pass # Inherits structure from BaseContextModel

class Decision(BaseModel):
    """Model for the decisions table."""
    id: Optional[int] = None # Auto-incremented by DB
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    summary: str
    rationale: Optional[str] = None
    implementation_details: Optional[str] = None

class ProgressEntry(BaseModel):
    """Model for the progress_entries table."""
    id: Optional[int] = None # Auto-incremented by DB
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str # e.g., 'TODO', 'IN_PROGRESS', 'DONE'
    description: str
    parent_id: Optional[int] = None # For subtasks

class SystemPattern(BaseModel):
    """Model for the system_patterns table."""
    id: Optional[int] = None # Auto-incremented by DB
    name: str # Should be unique
    description: Optional[str] = None

class CustomData(BaseModel):
    """Model for the custom_data table."""
    id: Optional[int] = None # Auto-incremented by DB
    category: str
    key: str
    value: Any # Store arbitrary JSON data (SQLAlchemy handles JSON str conversion for DB)

# --- MCP Tool Argument Models ---

class BaseArgs(BaseModel):
    """Base model for arguments requiring a workspace ID."""
    workspace_id: str = Field(..., description="Identifier for the workspace (e.g., absolute path)")

# --- Context Tools ---

class GetContextArgs(BaseArgs):
    """Arguments for getting product or active context (only workspace_id needed)."""
    pass

class UpdateContextArgs(BaseArgs):
    """Arguments for updating product or active context."""
    content: Dict[str, Any] = Field(..., description="The new context content as a dictionary")

# --- Decision Tools ---

class LogDecisionArgs(BaseArgs):
    """Arguments for logging a decision."""
    summary: str = Field(..., min_length=1, description="A concise summary of the decision")
    rationale: Optional[str] = Field(None, description="The reasoning behind the decision")
    implementation_details: Optional[str] = Field(None, description="Details about how the decision will be/was implemented")

class GetDecisionsArgs(BaseArgs):
    """Arguments for retrieving decisions."""
    limit: Optional[int] = Field(None, gt=0, description="Maximum number of decisions to return (most recent first)")

class SearchDecisionsArgs(BaseArgs):
    """Arguments for searching decisions using FTS."""
    query_term: str = Field(..., min_length=1, description="The term to search for in decisions.")
    limit: Optional[int] = Field(10, gt=0, description="Maximum number of search results to return.")

# --- Progress Tools ---

class LogProgressArgs(BaseArgs):
    """Arguments for logging a progress entry."""
    status: str = Field(..., description="Current status (e.g., 'TODO', 'IN_PROGRESS', 'DONE')")
    description: str = Field(..., min_length=1, description="Description of the progress or task")
    parent_id: Optional[int] = Field(None, description="ID of the parent task, if this is a subtask")

class GetProgressArgs(BaseArgs):
    """Arguments for retrieving progress entries."""
    status_filter: Optional[str] = Field(None, description="Filter entries by status")
    parent_id_filter: Optional[int] = Field(None, description="Filter entries by parent task ID")
    limit: Optional[int] = Field(None, gt=0, description="Maximum number of entries to return (most recent first)")

# --- System Pattern Tools ---

class LogSystemPatternArgs(BaseArgs):
    """Arguments for logging a system pattern."""
    name: str = Field(..., min_length=1, description="Unique name for the system pattern")
    description: Optional[str] = Field(None, description="Description of the pattern")

class GetSystemPatternsArgs(BaseArgs):
    """Arguments for retrieving system patterns (only workspace_id needed)."""
    pass

# --- Custom Data Tools ---

class LogCustomDataArgs(BaseArgs):
    """Arguments for logging custom data."""
    category: str = Field(..., min_length=1, description="Category for the custom data")
    key: str = Field(..., min_length=1, description="Key for the custom data (unique within category)")
    value: Any = Field(..., description="The custom data value (JSON serializable)")

class GetCustomDataArgs(BaseArgs):
    """Arguments for retrieving custom data."""
    category: Optional[str] = Field(None, description="Filter by category")
    key: Optional[str] = Field(None, description="Filter by key (requires category)")

class DeleteCustomDataArgs(BaseArgs):
    """Arguments for deleting custom data."""
    category: str = Field(..., min_length=1, description="Category of the data to delete")
    key: str = Field(..., min_length=1, description="Key of the data to delete")

class SearchProjectGlossaryArgs(BaseArgs):
    """Arguments for searching the ProjectGlossary using FTS."""
    query_term: str = Field(..., min_length=1, description="The term to search for in the glossary.")
    limit: Optional[int] = Field(10, gt=0, description="Maximum number of search results to return.")

# --- Export Tool ---

class ExportConportToMarkdownArgs(BaseArgs):
    """Arguments for exporting ConPort data to markdown files."""
    output_path: Optional[str] = Field(None, description="Optional output directory path relative to workspace_id. Defaults to './conport_export/' if not provided.")

# --- Import Tool ---

class ImportMarkdownToConportArgs(BaseArgs):
    """Arguments for importing markdown files into ConPort data."""
    input_path: Optional[str] = Field(None, description="Optional input directory path relative to workspace_id containing markdown files. Defaults to './conport_export/' if not provided.")

# Dictionary mapping tool names to their expected argument models (for potential future use/validation)
# Note: The primary validation happens in the handler using these models.
TOOL_ARG_MODELS = {
    "get_product_context": GetContextArgs,
    "update_product_context": UpdateContextArgs,
    "get_active_context": GetContextArgs,
    "update_active_context": UpdateContextArgs,
    "log_decision": LogDecisionArgs,
    "get_decisions": GetDecisionsArgs,
    "search_decisions_fts": SearchDecisionsArgs, # Added new tool
    "log_progress": LogProgressArgs,
    "get_progress": GetProgressArgs,
    "log_system_pattern": LogSystemPatternArgs,
    "get_system_patterns": GetSystemPatternsArgs,
    "log_custom_data": LogCustomDataArgs,
    "get_custom_data": GetCustomDataArgs,
    "delete_custom_data": DeleteCustomDataArgs,
    "search_project_glossary_fts": SearchProjectGlossaryArgs, # Added new tool
    "export_conport_to_markdown": ExportConportToMarkdownArgs,
    "import_markdown_to_conport": ImportMarkdownToConportArgs,
}