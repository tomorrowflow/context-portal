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

def handle_get_product_context(args: models.GetContextArgs) -> Dict[str, Any]:
    """
    Handles the 'get_product_context' MCP tool.
    Assumes 'args' is an already validated Pydantic model instance.
    """
    try:
        context_model = db.get_product_context(args.workspace_id)
        return context_model.content
    except DatabaseError as e:
        raise ContextPortalError(f"Database error getting product context: {e}")
    except Exception as e:
        # Log the full error for debugging if it's truly unexpected
        log.exception(f"Unexpected error in get_product_context for workspace {args.workspace_id}")
        raise ContextPortalError(f"Unexpected error in get_product_context: {e}")

def handle_update_product_context(args: models.UpdateContextArgs) -> Dict[str, Any]:
    """
    Handles the 'update_product_context' MCP tool.
    Assumes 'args' is an already validated Pydantic model instance.
    Returns a success message dictionary.
    """
    try:
        context_model = models.ProductContext(content=args.content) # content is already a dict
        db.update_product_context(args.workspace_id, context_model)
        # FastMCP expects direct results. A status message is a reasonable result.
        return {"status": "success", "message": "Product context updated successfully."}
    except ValidationError as e: # Should not happen if FastMCP validates schema, but good for direct calls
         raise ToolArgumentError(f"Invalid content structure: {e}")
    except DatabaseError as e:
        raise ContextPortalError(f"Database error updating product context: {e}")
    except Exception as e:
        log.exception(f"Unexpected error in update_product_context for workspace {args.workspace_id}")
        raise ContextPortalError(f"Unexpected error in update_product_context: {e}")

def handle_log_decision(args: models.LogDecisionArgs) -> Dict[str, Any]:
    """
    Handles the 'log_decision' MCP tool.
    Assumes 'args' is an already validated Pydantic model instance.
    Returns the logged decision as a dictionary.
    """
    try:
        decision_to_log = models.Decision(
            summary=args.summary,
            rationale=args.rationale,
            implementation_details=args.implementation_details
            # Timestamp is added automatically by the Pydantic model's default_factory
        )
        logged_decision = db.log_decision(args.workspace_id, decision_to_log)
        return logged_decision.model_dump(mode='json')
    except DatabaseError as e:
        raise ContextPortalError(f"Database error logging decision: {e}")
    except Exception as e:
        log.exception(f"Unexpected error in log_decision for workspace {args.workspace_id}")
        raise ContextPortalError(f"Unexpected error in log_decision: {e}")

# --- Added handlers --- # This comment might be outdated, these are just more handlers

def handle_get_decisions(args: models.GetDecisionsArgs) -> List[Dict[str, Any]]:
    """
    Handles the 'get_decisions' MCP tool.
    Assumes 'args' is an already validated Pydantic model instance.
    Returns a list of decision dictionaries.
    """
    try:
        decisions_list = db.get_decisions(args.workspace_id, limit=args.limit)
        return [d.model_dump(mode='json') for d in decisions_list]
    except DatabaseError as e:
        raise ContextPortalError(f"Database error getting decisions: {e}")
    except Exception as e:
        log.exception(f"Unexpected error in get_decisions for workspace {args.workspace_id}")
        raise ContextPortalError(f"Unexpected error in get_decisions: {e}")

def handle_search_decisions_fts(args: models.SearchDecisionsArgs) -> List[Dict[str, Any]]:
    """
    Handles the 'search_decisions_fts' MCP tool.
    Assumes 'args' is an already validated Pydantic model instance.
    Returns a list of decision dictionaries.
    """
    try:
        decisions_list = db.search_decisions_fts(
            args.workspace_id,
            query_term=args.query_term,
            limit=args.limit
        )
        return [d.model_dump(mode='json') for d in decisions_list]
    except DatabaseError as e:
        raise ContextPortalError(f"Database error searching decisions: {e}")
    except Exception as e:
        log.exception(f"Unexpected error in search_decisions_fts for workspace {args.workspace_id}")
        raise ContextPortalError(f"Unexpected error in search_decisions_fts: {e}")

def handle_get_active_context(args: models.GetContextArgs) -> Dict[str, Any]:
    """
    Handles the 'get_active_context' MCP tool.
    Assumes 'args' is an already validated Pydantic model instance.
    """
    try:
        context_model = db.get_active_context(args.workspace_id)
        return context_model.content
    except DatabaseError as e:
        raise ContextPortalError(f"Database error getting active context: {e}")
    except Exception as e:
        log.exception(f"Unexpected error in get_active_context for workspace {args.workspace_id}")
        raise ContextPortalError(f"Unexpected error in get_active_context: {e}")

def handle_update_active_context(args: models.UpdateContextArgs) -> Dict[str, Any]:
    """
    Handles the 'update_active_context' MCP tool.
    Assumes 'args' is an already validated Pydantic model instance.
    Returns a success message dictionary.
    """
    try:
        context_model = models.ActiveContext(content=args.content)
        db.update_active_context(args.workspace_id, context_model)
        return {"status": "success", "message": "Active context updated successfully."}
    except ValidationError as e: # Should not happen if FastMCP validates
         raise ToolArgumentError(f"Invalid content structure: {e}")
    except DatabaseError as e:
        raise ContextPortalError(f"Database error updating active context: {e}")
    except Exception as e:
        log.exception(f"Unexpected error in update_active_context for workspace {args.workspace_id}")
        raise ContextPortalError(f"Unexpected error in update_active_context: {e}")

def handle_log_progress(args: models.LogProgressArgs) -> Dict[str, Any]:
    """
    Handles the 'log_progress' MCP tool.
    Assumes 'args' is an already validated Pydantic model instance.
    Returns the logged progress entry as a dictionary.
    """
    try:
        progress_to_log = models.ProgressEntry(
            status=args.status,
            description=args.description,
            parent_id=args.parent_id
        )
        logged_progress = db.log_progress(args.workspace_id, progress_to_log)
        return logged_progress.model_dump(mode='json')
    except DatabaseError as e:
        raise ContextPortalError(f"Database error logging progress: {e}")
    except Exception as e:
        log.exception(f"Unexpected error in log_progress for workspace {args.workspace_id}")
        raise ContextPortalError(f"Unexpected error in log_progress: {e}")

def handle_get_progress(args: models.GetProgressArgs) -> List[Dict[str, Any]]:
    """
    Handles the 'get_progress' MCP tool.
    Assumes 'args' is an already validated Pydantic model instance.
    Returns a list of progress entry dictionaries.
    """
    try:
        progress_list = db.get_progress(
            args.workspace_id,
            status_filter=args.status_filter,
            parent_id_filter=args.parent_id_filter,
            limit=args.limit
        )
        return [p.model_dump(mode='json') for p in progress_list]
    except DatabaseError as e:
        raise ContextPortalError(f"Database error getting progress: {e}")
    except Exception as e:
        log.exception(f"Unexpected error in get_progress for workspace {args.workspace_id}")
        raise ContextPortalError(f"Unexpected error in get_progress: {e}")

def handle_log_system_pattern(args: models.LogSystemPatternArgs) -> Dict[str, Any]:
    """
    Handles the 'log_system_pattern' MCP tool.
    Assumes 'args' is an already validated Pydantic model instance.
    Returns the logged system pattern as a dictionary.
    """
    try:
        pattern_to_log = models.SystemPattern(name=args.name, description=args.description)
        logged_pattern = db.log_system_pattern(args.workspace_id, pattern_to_log)
        return logged_pattern.model_dump(mode='json')
    except DatabaseError as e:
        raise ContextPortalError(f"Database error logging system pattern: {e}")
    except Exception as e:
        log.exception(f"Unexpected error in log_system_pattern for workspace {args.workspace_id}")
        raise ContextPortalError(f"Unexpected error in log_system_pattern: {e}")

def handle_get_system_patterns(args: models.GetSystemPatternsArgs) -> List[Dict[str, Any]]:
    """
    Handles the 'get_system_patterns' MCP tool.
    Assumes 'args' is an already validated Pydantic model instance.
    Returns a list of system pattern dictionaries.
    """
    try:
        patterns_list = db.get_system_patterns(args.workspace_id)
        return [p.model_dump(mode='json') for p in patterns_list]
    except DatabaseError as e:
        raise ContextPortalError(f"Database error getting system patterns: {e}")
    except Exception as e:
        log.exception(f"Unexpected error in get_system_patterns for workspace {args.workspace_id}")
        raise ContextPortalError(f"Unexpected error in get_system_patterns: {e}")

def handle_log_custom_data(args: models.LogCustomDataArgs) -> Dict[str, Any]:
    """
    Handles the 'log_custom_data' MCP tool.
    Assumes 'args' is an already validated Pydantic model instance.
    Returns the logged custom data entry as a dictionary.
    """
    try:
        data_to_log = models.CustomData(category=args.category, key=args.key, value=args.value)
        logged_data = db.log_custom_data(args.workspace_id, data_to_log)
        return logged_data.model_dump(mode='json')
    except DatabaseError as e:
        raise ContextPortalError(f"Database error logging custom data: {e}")
    except Exception as e:
        log.exception(f"Unexpected error in log_custom_data for workspace {args.workspace_id}")
        raise ContextPortalError(f"Unexpected error in log_custom_data: {e}")

def handle_get_custom_data(args: models.GetCustomDataArgs) -> List[Dict[str, Any]]:
    """
    Handles the 'get_custom_data' MCP tool.
    Assumes 'args' is an already validated Pydantic model instance.
    Returns a list of custom data entry dictionaries.
    """
    try:
        data_list = db.get_custom_data(args.workspace_id, category=args.category, key=args.key)
        return [d.model_dump(mode='json') for d in data_list]
    except ValueError as e: # From db function if key w/o category, or other validation
         raise ToolArgumentError(str(e)) # Pass specific error message
    except DatabaseError as e:
        raise ContextPortalError(f"Database error getting custom data: {e}")
    except Exception as e:
        log.exception(f"Unexpected error in get_custom_data for workspace {args.workspace_id}")
        raise ContextPortalError(f"Unexpected error in get_custom_data: {e}")

def handle_delete_custom_data(args: models.DeleteCustomDataArgs) -> Dict[str, Any]:
    """
    Handles the 'delete_custom_data' MCP tool.
    Assumes 'args' is an already validated Pydantic model instance.
    Returns a status message dictionary.
    """
    try:
        deleted = db.delete_custom_data(args.workspace_id, category=args.category, key=args.key)
        if deleted:
            return {"status": "success", "message": f"Custom data '{args.category}/{args.key}' deleted."}
        else:
            return {"status": "success", "message": f"Custom data '{args.category}/{args.key}' not found for deletion."}
    except DatabaseError as e:
        raise ContextPortalError(f"Database error deleting custom data: {e}")
    except Exception as e:
        log.exception(f"Unexpected error in delete_custom_data for workspace {args.workspace_id}")
        raise ContextPortalError(f"Unexpected error in delete_custom_data: {e}")

def handle_search_project_glossary_fts(args: models.SearchProjectGlossaryArgs) -> List[Dict[str, Any]]:
    """
    Handles the 'search_project_glossary_fts' MCP tool.
    Assumes 'args' is an already validated Pydantic model instance.
    Returns a list of glossary entry dictionaries.
    """
    try:
        glossary_entries = db.search_project_glossary_fts(
            args.workspace_id,
            query_term=args.query_term,
            limit=args.limit
        )
        return [entry.model_dump(mode='json') for entry in glossary_entries]
    except DatabaseError as e:
        raise ContextPortalError(f"Database error searching project glossary: {e}")
    except Exception as e:
        log.exception(f"Unexpected error in search_project_glossary_fts for workspace {args.workspace_id}")
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

def handle_export_conport_to_markdown(args: models.ExportConportToMarkdownArgs) -> Dict[str, Any]:
    """
    Exports all ConPort data for a workspace to markdown files.
    Assumes 'args' is an already validated Pydantic model instance.
    """
    workspace_path = Path(args.workspace_id)
    output_dir_name = args.output_path if args.output_path else "conport_export"
    output_path = workspace_path / output_dir_name

    try:
        output_path.mkdir(parents=True, exist_ok=True)
        log.info(f"Exporting ConPort data for workspace '{args.workspace_id}' to '{output_path}'")

        files_created = []

        # Product Context
        product_ctx_data = db.get_product_context(args.workspace_id).content
        if product_ctx_data:
            (output_path / "product_context.md").write_text(_format_product_context_md(product_ctx_data))
            files_created.append("product_context.md")

        # Active Context
        active_ctx_data = db.get_active_context(args.workspace_id).content
        if active_ctx_data:
            (output_path / "active_context.md").write_text(_format_active_context_md(active_ctx_data))
            files_created.append("active_context.md")
        
        # Decisions
        decisions = db.get_decisions(args.workspace_id, limit=None) # Get all
        if decisions:
            (output_path / "decision_log.md").write_text(_format_decisions_md(decisions))
            files_created.append("decision_log.md")

        # Progress
        progress_entries = db.get_progress(args.workspace_id, limit=None) # Get all
        if progress_entries:
            (output_path / "progress_log.md").write_text(_format_progress_md(progress_entries))
            files_created.append("progress_log.md")

        # System Patterns
        system_patterns = db.get_system_patterns(args.workspace_id)
        if system_patterns:
            (output_path / "system_patterns.md").write_text(_format_system_patterns_md(system_patterns))
            files_created.append("system_patterns.md")

        # Custom Data
        custom_data_entries = db.get_custom_data(args.workspace_id)
        if custom_data_entries:
            custom_data_path = output_path / "custom_data"
            custom_data_path.mkdir(exist_ok=True)
            categories: Dict[str, List[str]] = {}
            for item in custom_data_entries:
                if item.category not in categories:
                    categories[item.category] = []
                
                value_str = json.dumps(item.value, indent=2) if not isinstance(item.value, str) else item.value
                categories[item.category].append(f"### {item.key}\n\n```json\n{value_str}\n```\n")
            
            for category_name_from_loop, items_md in categories.items(): # Renamed category to avoid clash
                cat_file_name = "".join(c if c.isalnum() else "_" for c in category_name_from_loop) + ".md"
                (custom_data_path / cat_file_name).write_text(f"# Custom Data: {category_name_from_loop}\n\n" + "\n---\n".join(items_md))
                files_created.append(f"custom_data/{cat_file_name}")
        
        return {"status": "success", "message": f"ConPort data exported to '{output_path}'. Files created: {', '.join(files_created)}"}

    except DatabaseError as e:
        raise ContextPortalError(f"Database error during export: {e}")
    except IOError as e:
        raise ContextPortalError(f"File system error during export to '{output_path}': {e}")
    except Exception as e:
        log.exception(f"Unexpected error in export_conport_to_markdown for workspace {args.workspace_id}")
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


def handle_import_markdown_to_conport(args: models.ImportMarkdownToConportArgs) -> Dict[str, Any]:
    """
    Imports data from markdown files into ConPort for a workspace.
    Assumes 'args' is an already validated Pydantic model instance.
    """
    workspace_path = Path(args.workspace_id)
    input_dir_name = args.input_path if args.input_path else "conport_export"
    input_path = workspace_path / input_dir_name

    if not input_path.is_dir():
        raise ToolArgumentError(f"Input directory not found: {input_path}")

    log.info(f"Importing ConPort data for workspace '{args.workspace_id}' from '{input_path}'")
    summary_report = {"status": "success", "message": "Import process initiated.", "files_processed": [], "items_logged": {}, "errors": []}

    # This handler will be called by a tool wrapper in main.py.
    # It calls other refactored handlers in this file.
    
    # Define which handler and Pydantic model to use for each file type
    file_processing_map = {
        "product_context.md": (_parse_product_or_active_context_md, handle_update_product_context, models.UpdateContextArgs),
        "active_context.md": (_parse_product_or_active_context_md, handle_update_active_context, models.UpdateContextArgs),
        "decision_log.md": (_parse_decisions_md, handle_log_decision, models.LogDecisionArgs),
        "progress_log.md": (_parse_progress_md, handle_log_progress, models.LogProgressArgs),
        "system_patterns.md": (_parse_system_patterns_md, handle_log_system_pattern, models.LogSystemPatternArgs),
    }

    for filename, (parser_func, target_handler_func, pydantic_arg_model) in file_processing_map.items():
        file_to_import = input_path / filename
        if file_to_import.is_file():
            try:
                content_str = file_to_import.read_text(encoding="utf-8")
                parsed_data = parser_func(content_str)
                summary_report["files_processed"].append(filename)
                
                item_type_key = filename.split('.')[0] # Define item_type_key

                if item_type_key in ["product_context", "active_context"]:
                    # For these, parsed_data is the content dict itself
                    handler_call_args = pydantic_arg_model(workspace_id=args.workspace_id, content=parsed_data)
                    target_handler_func(handler_call_args)
                    summary_report["items_logged"][item_type_key] = summary_report["items_logged"].get(item_type_key, 0) + 1
                else: # List based items (decisions, progress, system_patterns)
                    for item_data in parsed_data: # parsed_data is a list of dicts
                        handler_call_args = pydantic_arg_model(workspace_id=args.workspace_id, **item_data)
                        target_handler_func(handler_call_args)
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
        for category_md_file in custom_data_dir.glob("*.md"): # Renamed variable
            try:
                category_name = category_md_file.stem.replace("_", " ")
                content_str = category_md_file.read_text(encoding="utf-8")
                parsed_custom_items = _parse_custom_data_category_md(content_str, category_name)
                for item_data in parsed_custom_items:
                    # item_data already contains 'category', 'key', 'value'
                    handler_args = models.LogCustomDataArgs(workspace_id=args.workspace_id, **item_data)
                    handle_log_custom_data(handler_args)
                    summary_report["items_logged"]["custom_data"] = summary_report["items_logged"].get("custom_data", 0) + 1
            except Exception as e:
                log.error(f"Error processing custom data file {category_md_file.name}: {e}")
                summary_report["errors"].append(f"Error processing {category_md_file.name}: {str(e)}")
    
    summary_report["message"] = f"ConPort data import from '{input_path}' complete. See details."
    return summary_report

# --- Obsolete MCP Dispatcher Logic ---
# The following (TOOL_DESCRIPTIONS, handle_list_tools, TOOL_HANDLERS, dispatch_tool)
# are now obsolete as FastMCP handles tool registration, listing, and dispatch.
# They are removed to prevent confusion and ensure the new FastMCP mechanism is used.