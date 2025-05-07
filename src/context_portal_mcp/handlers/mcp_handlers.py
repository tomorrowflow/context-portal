"""Functions implementing the logic for each MCP tool."""

import logging
import os
from pathlib import Path
import json
import re # For markdown parsing
from typing import Dict, Any, List, Optional

from pydantic import ValidationError

from ..db import database as db
from ..db import models
from ..core.exceptions import ToolArgumentError, DatabaseError, ContextPortalError

log = logging.getLogger(__name__) # Add logger instance

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

def handle_search_decisions_fts(arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Handles the 'search_decisions_fts' MCP tool."""
    try:
        args_model = models.SearchDecisionsArgs(**arguments)
    except ValidationError as e:
        raise ToolArgumentError(f"Invalid arguments for search_decisions_fts: {e}")

    try:
        decisions_list = db.search_decisions_fts(
            args_model.workspace_id,
            query_term=args_model.query_term,
            limit=args_model.limit
        )
        return [d.model_dump(mode='json') for d in decisions_list]
    except DatabaseError as e:
        raise ContextPortalError(f"Database error searching decisions: {e}")
    except Exception as e:
        raise ContextPortalError(f"Unexpected error in search_decisions_fts: {e}")

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

def handle_search_project_glossary_fts(arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Handles the 'search_project_glossary_fts' MCP tool."""
    try:
        args_model = models.SearchProjectGlossaryArgs(**arguments)
    except ValidationError as e:
        raise ToolArgumentError(f"Invalid arguments for search_project_glossary_fts: {e}")

    try:
        glossary_entries = db.search_project_glossary_fts(
            args_model.workspace_id,
            query_term=args_model.query_term,
            limit=args_model.limit
        )
        # Results are already models.CustomData, so model_dump them
        return [entry.model_dump(mode='json') for entry in glossary_entries]
    except DatabaseError as e:
        raise ContextPortalError(f"Database error searching project glossary: {e}")
    except Exception as e:
        raise ContextPortalError(f"Unexpected error in search_project_glossary_fts: {e}")

# --- Export Tool Handler ---

def _format_product_context_md(data: Dict[str, Any]) -> str:
    lines = ["# Product Context\n"]
    for key, value in data.items():
        heading = key.replace("_", " ").title()
        lines.append(f"## {heading}\n")
        if isinstance(value, str):
            lines.append(value.strip() + "\n")
        elif isinstance(value, list):
            for item in value:
                lines.append(f"*   {item}\n")
        else: # Fallback for other types
            lines.append(str(value) + "\n")
        lines.append("\n")
    return "".join(lines)

def _format_active_context_md(data: Dict[str, Any]) -> str:
    lines = ["# Active Context\n"]
    # Expected keys: introduction, currentFocus, recentChanges, openQuestionsIssues
    if data.get("introduction"):
        lines.append(data["introduction"].strip() + "\n\n")
    
    if data.get("currentFocus"):
        lines.append("## Current Focus\n")
        lines.append(data["currentFocus"].strip() + "\n\n")
    
    if data.get("recentChanges"):
        lines.append("## Recent Changes\n")
        lines.append(data["recentChanges"].strip() + "\n\n")

    if data.get("openQuestionsIssues"):
        lines.append("## Open Questions/Issues\n")
        lines.append(data["openQuestionsIssues"].strip() + "\n\n")
    return "".join(lines)

def _format_decisions_md(decisions: List[models.Decision]) -> str:
    lines = ["# Decision Log\n"]
    for dec in sorted(decisions, key=lambda x: x.timestamp, reverse=True):
        lines.append("\n---\n")
        lines.append("## Decision\n")
        lines.append(f"*   [{dec.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {dec.summary}\n")
        if dec.rationale:
            lines.append("\n## Rationale\n")
            lines.append(f"*   {dec.rationale}\n")
        if dec.implementation_details:
            lines.append("\n## Implementation Details\n")
            lines.append(f"*   {dec.implementation_details}\n")
    return "".join(lines)

def _format_progress_md(progress_entries: List[models.ProgressEntry]) -> str:
    lines = ["# Progress Log\n"]
    status_map = {"DONE": [], "IN_PROGRESS": [], "TODO": []}
    for entry in sorted(progress_entries, key=lambda x: x.timestamp, reverse=True):
        status_map.get(entry.status, status_map["TODO"]).append(entry)

    if status_map["DONE"]:
        lines.append("\n## Completed Tasks\n")
        for entry in status_map["DONE"]:
            lines.append(f"*   [{entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {entry.description}\n")
    if status_map["IN_PROGRESS"]:
        lines.append("\n## In Progress Tasks\n")
        for entry in status_map["IN_PROGRESS"]:
            lines.append(f"*   [{entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {entry.description}\n")
    if status_map["TODO"]:
        lines.append("\n## TODO Tasks\n")
        for entry in status_map["TODO"]:
            lines.append(f"*   [{entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {entry.description}\n")
    return "".join(lines)

def _format_system_patterns_md(patterns: List[models.SystemPattern]) -> str:
    lines = ["# System Patterns\n"]
    for pattern in sorted(patterns, key=lambda x: x.name):
        lines.append(f"\n## {pattern.name}\n")
        if pattern.description:
            lines.append(f"{pattern.description}\n")
    return "".join(lines)

def handle_export_conport_to_markdown(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Exports all ConPort data for a workspace to markdown files."""
    try:
        args_model = models.ExportConportToMarkdownArgs(**arguments)
    except ValidationError as e:
        raise ToolArgumentError(f"Invalid arguments for export_conport_to_markdown: {e}")

    workspace_path = Path(args_model.workspace_id)
    output_dir_name = args_model.output_path if args_model.output_path else "conport_export"
    output_path = workspace_path / output_dir_name

    try:
        output_path.mkdir(parents=True, exist_ok=True)
        log.info(f"Exporting ConPort data for workspace '{args_model.workspace_id}' to '{output_path}'")

        files_created = []

        # Product Context
        product_ctx_data = db.get_product_context(args_model.workspace_id).content
        if product_ctx_data:
            (output_path / "product_context.md").write_text(_format_product_context_md(product_ctx_data))
            files_created.append("product_context.md")

        # Active Context
        active_ctx_data = db.get_active_context(args_model.workspace_id).content
        if active_ctx_data:
            (output_path / "active_context.md").write_text(_format_active_context_md(active_ctx_data))
            files_created.append("active_context.md")
        
        # Decisions
        decisions = db.get_decisions(args_model.workspace_id, limit=None) # Get all
        if decisions:
            (output_path / "decision_log.md").write_text(_format_decisions_md(decisions))
            files_created.append("decision_log.md")

        # Progress
        progress_entries = db.get_progress(args_model.workspace_id, limit=None) # Get all
        if progress_entries:
            (output_path / "progress_log.md").write_text(_format_progress_md(progress_entries))
            files_created.append("progress_log.md")

        # System Patterns
        system_patterns = db.get_system_patterns(args_model.workspace_id)
        if system_patterns:
            (output_path / "system_patterns.md").write_text(_format_system_patterns_md(system_patterns))
            files_created.append("system_patterns.md")

        # Custom Data
        custom_data_entries = db.get_custom_data(args_model.workspace_id)
        if custom_data_entries:
            custom_data_path = output_path / "custom_data"
            custom_data_path.mkdir(exist_ok=True)
            categories: Dict[str, List[str]] = {}
            for item in custom_data_entries:
                if item.category not in categories:
                    categories[item.category] = []
                
                value_str = json.dumps(item.value, indent=2) if not isinstance(item.value, str) else item.value
                categories[item.category].append(f"### {item.key}\n\n```json\n{value_str}\n```\n")
            
            for category, items_md in categories.items():
                cat_file_name = "".join(c if c.isalnum() else "_" for c in category) + ".md"
                (custom_data_path / cat_file_name).write_text(f"# Custom Data: {category}\n\n" + "\n---\n".join(items_md))
                files_created.append(f"custom_data/{cat_file_name}")
        
        return {"status": "success", "message": f"ConPort data exported to '{output_path}'. Files created: {', '.join(files_created)}"}

    except DatabaseError as e:
        raise ContextPortalError(f"Database error during export: {e}")
    except IOError as e:
        raise ContextPortalError(f"File system error during export to '{output_path}': {e}")
    except Exception as e:
        log.exception(f"Unexpected error in export_conport_to_markdown for workspace {args_model.workspace_id}")
        raise ContextPortalError(f"Unexpected error during export: {e}")

# --- Import Tool Handler ---

def _parse_key_value_markdown_section(section_content: str) -> str:
    """Helper to extract content from a simple markdown section."""
    lines = [line.strip() for line in section_content.strip().split('\n') if line.strip()]
    # Remove potential list markers like '* '
    cleaned_lines = [re.sub(r"^\*   ", "", line) for line in lines]
    return "\n".join(cleaned_lines).strip()

def _parse_product_or_active_context_md(content: str) -> Dict[str, Any]:
    """Parses product_context.md or active_context.md content."""
    data = {}
    # Split by '## ' to get sections, ignoring the initial '# Title' part
    sections = re.split(r'\n## ', content)[1:]
    
    # First section is usually an introduction before the first '## '
    intro_match = re.match(r'^#\s\w+\sContext\n+(.*?)\n## ', content, re.DOTALL | re.MULTILINE)
    if intro_match:
        data["introduction"] = intro_match.group(1).strip()

    for section in sections:
        parts = section.split('\n', 1)
        heading_full = parts[0].strip()
        section_content = parts[1] if len(parts) > 1 else ""
        
        # Create a key from the heading (e.g., "Project Goal" -> "projectGoal")
        key = heading_full.replace(" ", "")
        key = key[0].lower() + key[1:] if key else ""

        if key: # Ensure key is not empty
             # For "Recent Changes", we expect a list-like structure.
            if "Recent Changes" in heading_full:
                 data[key] = _parse_key_value_markdown_section(section_content) # Keep as single string
            else:
                data[key] = _parse_key_value_markdown_section(section_content)
    return data

def _parse_decisions_md(content: str) -> List[Dict[str, str]]:
    """Parses decision_log.md content."""
    decisions = []
    # Split by '---' separator, then process each decision block
    decision_blocks = content.split('\n---\n')
    for block in decision_blocks:
        if not block.strip() or "## Decision" not in block :
            continue
        
        summary_match = re.search(r"## Decision\n\*\s*\[.*?\]\s*(.+)", block, re.DOTALL)
        summary = summary_match.group(1).strip() if summary_match else "N/A"
        
        rationale_match = re.search(r"## Rationale\n\*\s*(.+)", block, re.DOTALL)
        rationale = rationale_match.group(1).strip() if rationale_match else None
        # Handle multi-line rationale
        if rationale_match and '\n*' in rationale: # crude check for multi-bullet rationale
            rationale = "\n".join([line.strip().lstrip('*').strip() for line in rationale.split('\n')])


        impl_details_match = re.search(r"## Implementation Details\n\*\s*(.+)", block, re.DOTALL)
        impl_details = impl_details_match.group(1).strip() if impl_details_match else None
        if impl_details_match and '\n*' in impl_details: # crude check for multi-bullet details
            impl_details = "\n".join([line.strip().lstrip('*').strip() for line in impl_details.split('\n')])

        decisions.append({
            "summary": summary,
            "rationale": rationale,
            "implementation_details": impl_details
        })
    return decisions

def _parse_progress_md(content: str) -> List[Dict[str, str]]:
    """Parses progress_log.md content."""
    progress_items = []
    current_status = "TODO" # Default
    
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith("## Completed Tasks"):
            current_status = "DONE"
        elif line.startswith("## In Progress Tasks") or line.startswith("## Current Tasks"):
            current_status = "IN_PROGRESS"
        elif line.startswith("## TODO Tasks") or line.startswith("## Next Steps"):
            current_status = "TODO"
        elif line.startswith("*"):
            description = re.sub(r"^\*\s*(\[.*?\]\s*)?", "", line).strip()
            if description:
                progress_items.append({"status": current_status, "description": description})
    return progress_items

def _parse_system_patterns_md(content: str) -> List[Dict[str, str]]:
    """Parses system_patterns.md content."""
    patterns = []
    current_name = None
    current_desc_lines = []

    for line in content.split('\n'):
        line = line.strip()
        if line.startswith("## "):
            if current_name: # Save previous pattern
                patterns.append({"name": current_name, "description": "\n".join(current_desc_lines).strip() or None})
                current_desc_lines = []
            current_name = line[3:].strip()
        elif current_name and line and not line.startswith("#"):
            current_desc_lines.append(line)
    
    if current_name: # Save the last pattern
        patterns.append({"name": current_name, "description": "\n".join(current_desc_lines).strip() or None})
    return patterns

def _parse_custom_data_category_md(content: str, category_name: str) -> List[Dict[str, Any]]:
    """Parses a custom_data category markdown file."""
    items = []
    # Split by '### ' for keys, then parse the JSON block
    key_blocks = re.split(r'\n### ', content)
    for block in key_blocks:
        if not block.strip() or "```json" not in block:
            continue
        
        key_match = re.match(r"(.+?)\n+```json\n(.*?)\n```", block.strip(), re.DOTALL | re.MULTILINE)
        if key_match:
            key = key_match.group(1).strip()
            json_str_value = key_match.group(2).strip()
            try:
                value = json.loads(json_str_value)
                items.append({"category": category_name, "key": key, "value": value})
            except json.JSONDecodeError as e:
                log.warning(f"Could not parse JSON for custom data {category_name}/{key}: {e}. Value: '{json_str_value}'")
    return items


def handle_import_markdown_to_conport(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Imports data from markdown files into ConPort for a workspace."""
    try:
        args_model = models.ImportMarkdownToConportArgs(**arguments)
    except ValidationError as e:
        raise ToolArgumentError(f"Invalid arguments for import_markdown_to_conport: {e}")

    workspace_path = Path(args_model.workspace_id)
    input_dir_name = args_model.input_path if args_model.input_path else "conport_export" # Default to export dir
    input_path = workspace_path / input_dir_name

    if not input_path.is_dir():
        raise ToolArgumentError(f"Input directory not found: {input_path}")

    log.info(f"Importing ConPort data for workspace '{args_model.workspace_id}' from '{input_path}'")
    summary_report = {"status": "success", "message": "Import process initiated.", "files_processed": [], "items_logged": {}, "errors": []}

    file_parsers = {
        "product_context.md": (_parse_product_or_active_context_md, "update_product_context", "product_context"),
        "active_context.md": (_parse_product_or_active_context_md, "update_active_context", "active_context"),
        "decision_log.md": (_parse_decisions_md, "log_decision", "decisions"),
        "progress_log.md": (_parse_progress_md, "log_progress", "progress_entries"),
        "system_patterns.md": (_parse_system_patterns_md, "log_system_pattern", "system_patterns"),
    }

    for filename, (parser_func, tool_name, item_type_key) in file_parsers.items():
        file_to_import = input_path / filename
        if file_to_import.is_file():
            try:
                content_str = file_to_import.read_text(encoding="utf-8")
                parsed_data = parser_func(content_str)
                summary_report["files_processed"].append(filename)
                
                if item_type_key in ["product_context", "active_context"]:
                    db_tool_args = {"workspace_id": args_model.workspace_id, "content": parsed_data}
                    TOOL_HANDLERS[tool_name](db_tool_args) # Call handler directly
                    summary_report["items_logged"][item_type_key] = summary_report["items_logged"].get(item_type_key, 0) + 1
                else: # List based items
                    for item_data in parsed_data:
                        db_tool_args = {"workspace_id": args_model.workspace_id, **item_data}
                        TOOL_HANDLERS[tool_name](db_tool_args) # Call handler directly
                        summary_report["items_logged"][item_type_key] = summary_report["items_logged"].get(item_type_key, 0) + 1
            except Exception as e:
                log.error(f"Error processing file {filename}: {e}")
                summary_report["errors"].append(f"Error processing {filename}: {str(e)}")
        else:
            log.warning(f"File not found for import: {file_to_import}")
            summary_report["errors"].append(f"File not found: {filename}")
            
    # Custom Data
    custom_data_dir = input_path / "custom_data"
    if custom_data_dir.is_dir():
        summary_report["files_processed"].append("custom_data/*")
        for category_file in custom_data_dir.glob("*.md"):
            try:
                category_name = category_file.stem.replace("_", " ") # Recreate category name
                content_str = category_file.read_text(encoding="utf-8")
                parsed_items = _parse_custom_data_category_md(content_str, category_name)
                for item_data in parsed_items:
                    # 'category' is already in item_data from parser
                    db_tool_args = {"workspace_id": args_model.workspace_id, **item_data}
                    TOOL_HANDLERS["log_custom_data"](db_tool_args)
                    summary_report["items_logged"]["custom_data"] = summary_report["items_logged"].get("custom_data", 0) + 1
            except Exception as e:
                log.error(f"Error processing custom data file {category_file.name}: {e}")
                summary_report["errors"].append(f"Error processing {category_file.name}: {str(e)}")
    
    summary_report["message"] = f"ConPort data import from '{input_path}' complete. See details."
    return summary_report

# --- ListTools Handler ---

# Simple descriptions for now, could be enhanced
TOOL_DESCRIPTIONS = {
    "get_product_context": "Retrieves the overall project context from ConPort (Context Portal).",
    "update_product_context": "Updates the overall project context in ConPort (Context Portal).",
    "get_active_context": "Retrieves the current working context (focus, recent changes, issues) from ConPort.",
    "update_active_context": "Updates the current working context in ConPort.",
    "log_decision": "Logs an architectural or implementation decision to ConPort.",
    "get_decisions": "Retrieves logged decisions from ConPort, optionally limited.",
    "search_decisions_fts": "Searches decisions using Full-Text Search for a given query term.",
    "log_progress": "Logs a progress entry or task status to ConPort.",
    "get_progress": "Retrieves progress entries from ConPort, optionally filtered.",
    "log_system_pattern": "Logs or updates a system/coding pattern used in the project to ConPort.",
    "get_system_patterns": "Retrieves all logged system patterns from ConPort.",
    "log_custom_data": "Stores or updates a custom key-value data entry under a category in ConPort.",
    "get_custom_data": "Retrieves custom data entries from ConPort, optionally filtered by category/key.",
    "delete_custom_data": "Deletes a specific custom data entry from ConPort.",
    "search_project_glossary_fts": "Searches the ProjectGlossary (custom data category) using Full-Text Search.",
    "export_conport_to_markdown": "Exports all ConPort data for a workspace to markdown files in a specified output directory (defaults to './conport_export/')."
}

def handle_list_tools(arguments: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """Handles the ListTools MCP request. Ignores arguments."""
    tool_list = []
    # Iterate through the argument models defined in models.py
    for tool_name, model_cls in models.TOOL_ARG_MODELS.items():
        try:
            # Generate JSON schema from the Pydantic model
            schema = model_cls.model_json_schema()
            # Remove the 'title' which defaults to model name, often not needed
            schema.pop("title", None)
            # Get description (can be improved)
            description = TOOL_DESCRIPTIONS.get(tool_name, f"Handler for {tool_name}")

            tool_list.append({
                "name": tool_name,
                "description": description,
                "inputSchema": schema
            })
        except Exception as e:
            # Log error generating schema for a specific tool
            log.error(f"Error generating schema for tool {tool_name}: {e}", exc_info=True) # Use logger
            # print(f"Error generating schema for tool {tool_name}: {e}") # Keep commented out
            continue # Skip this tool if schema generation fails

    return {"tools": tool_list}


# --- Tool Dispatcher ---

# A dictionary mapping tool names to their handler functions
TOOL_HANDLERS = {
    "ListTools": handle_list_tools, # Added ListTools handler
    "get_product_context": handle_get_product_context,
    "update_product_context": handle_update_product_context,
    "get_active_context": handle_get_active_context,
    "update_active_context": handle_update_active_context,
    "log_decision": handle_log_decision,
    "get_decisions": handle_get_decisions,
    "search_decisions_fts": handle_search_decisions_fts, # Added new handler
    "log_progress": handle_log_progress,
    "get_progress": handle_get_progress,
    "log_system_pattern": handle_log_system_pattern,
    "get_system_patterns": handle_get_system_patterns,
    "log_custom_data": handle_log_custom_data,
    "get_custom_data": handle_get_custom_data,
    "delete_custom_data": handle_delete_custom_data,
    "search_project_glossary_fts": handle_search_project_glossary_fts, # Added new handler
    "export_conport_to_markdown": handle_export_conport_to_markdown,
    "import_markdown_to_conport": handle_import_markdown_to_conport,
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