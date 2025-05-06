# Context Portal MCP (ConPort)

A database-backed Model Context Protocol (MCP) server for managing structured project context, designed to be used by AI assistants and developer tools within IDEs and other interfaces.

## Overview

This project is the **Context Portal MCP server (ConPort)**. ConPort provides a robust and structured way for AI assistants to store, retrieve, and manage various types of project context (e.g., product goals, active tasks, decisions, progress, architectural patterns, custom data) via a dedicated MCP server.

It can replace older file-based context management systems by offering a more reliable and queryable database backend (SQLite per workspace). ConPort is designed to be a generic context backend, compatible with various IDEs and client interfaces that support MCP.

Key features include:
*   Structured context storage using SQLite (one DB per workspace).
*   MCP server (`context_portal_mcp`) built with Python/FastAPI.
*   Defined MCP tools for interaction (e.g., `log_decision`, `get_active_context`).
*   Multi-workspace support via `workspace_id`.
*   Dual deployment modes: Stdio and Local HTTP.

## Setup & Installation

It is recommended to use `uv` for Python environment and package management.

1.  **Create and activate a virtual environment (if you haven't already):**
    ```bash
    uv venv
    source .venv/bin/activate  # Linux/macOS
    # .venv\Scripts\activate  # Windows
    ```

2.  **Install dependencies:**
    ```bash
    uv pip install -r requirements.txt
    ```

## Running the ConPort Server

The ConPort server can be run in two primary modes:

### 1. STDIO Mode (Recommended for IDE Integration)

This mode is ideal for tight integration with an IDE (like Roo Code), where the IDE spawns and manages the server process for the current workspace.

*   **Command:**
    ```bash
    uv run python src/context_portal_mcp/main.py --mode stdio --workspace_id "/actual/path/to/your/project_workspace"
    ```
*   Replace `"/actual/path/to/your/project_workspace"` with the absolute path to the workspace whose context you want ConPort to manage. The IDE typically provides this path dynamically (e.g., via a variable like `${workspaceFolder}`).
*   ConPort will create/use a database file at `your_project_workspace/.context_portal/data.sqlite`.

### 2. HTTP Mode (for Broader Access or Standalone Use)

This mode runs ConPort as an HTTP server, making it accessible over the network.

*   **Command:**
    ```bash
    uv run python src/context_portal_mcp/main.py --mode http --host 127.0.0.1 --port 8123
    ```
*   This starts the server on `http://127.0.0.1:8123`. The JSON-RPC endpoint will be `/mcp`.
*   When using HTTP mode, ensure the `workspace_id` is correctly passed by clients in their tool call arguments, as the server itself doesn't have an inherent workspace context when run standalone like this (unless a default is implemented or configured via environment variables, which is not the current setup).

## Client Configuration

MCP clients (like IDE extensions or other tools) need to be configured to connect to a running ConPort instance. Here are example configurations:

### For STDIO Mode (e.g., in Roo Code's `.vscode/mcp.json` or global settings)

This tells the IDE how to launch the ConPort server for the current workspace.

```json
{
  "mcpServers": {
    "conport_stdio": {
      "name": "Context Portal (ConPort) - STDIO",
      "description": "Manages project context for the current workspace.",
      "command": "uv",
      "args": [
        "run",
        "python",
        "/path/to/your/context-portal-mcp-repo/src/context_portal_mcp/main.py",
        "--mode",
        "stdio",
        "--workspace_id",
        "${workspaceFolder}"
      ],
      "cwd": "/path/to/your/context-portal-mcp-repo", // Should be the root of THIS ConPort server project
      "disabled": false,
      "alwaysAllow": [] // Optionally list tool names to bypass user confirmation
    }
  }
}
```
*   **Important:** Replace `/path/to/your/context-portal-mcp-repo` with the actual absolute path to where you have cloned *this* ConPort server project.
*   `${workspaceFolder}` is a common IDE variable representing the root of the project the user currently has open (for which ConPort will manage context).

### For HTTP Mode (Clients connecting to an already running HTTP server)

```json
{
  "mcpServers": {
    "conport_http": {
      "name": "Context Portal (ConPort) - HTTP",
      "description": "Connects to a running ConPort HTTP server.",
      "url": "http://127.0.0.1:8123/mcp", // Default URL
      "disabled": false,
      "alwaysAllow": []
    }
  }
}
```

## Usage with LLM Agents (via `conport_memory_strategy.yml`)

The `conport_memory_strategy.yml` file in this repository provides a comprehensive set of custom instructions for LLM agents. These instructions guide an agent on how to:

*   **Initialize Context:** At the start of a session, load existing project information (product overview, active tasks, decisions, etc.) from ConPort using its `get_*` tools.
*   **Update Context:** Throughout a session, as new information is generated or decisions are made, use ConPort's `log_*` and `update_*` tools to save this context persistently.
*   **Manage Custom Data:** Store and retrieve project-specific information that doesn't fit the standard context categories using `log_custom_data` and `get_custom_data`.
*   **Follow Triggers:** Understand when and how to update different aspects of the project's memory in ConPort.

By equipping an LLM agent with these instructions (typically as part of its system prompt) and connecting it to a running ConPort server for the relevant workspace, the agent can maintain a structured and persistent understanding of the project, leading to more informed and context-aware assistance.
The `workspace_id` is crucial for all ConPort tool interactions to ensure the agent is working with the correct project's data.

## Available ConPort Tools

The ConPort server exposes the following tools via MCP. All tools require a `workspace_id` argument (string, required) to specify the target project workspace.

*   **`get_product_context`**
    *   Description: Retrieves the overall project context from ConPort (Context Portal).
    *   Arguments: `workspace_id` (string, required).
*   **`update_product_context`**
    *   Description: Updates the overall project context in ConPort (Context Portal).
    *   Arguments: `workspace_id` (string, required), `content` (object, required - a JSON object representing the new product context).
*   **`get_active_context`**
    *   Description: Retrieves the current working context (focus, recent changes, issues) from ConPort.
    *   Arguments: `workspace_id` (string, required).
*   **`update_active_context`**
    *   Description: Updates the current working context in ConPort.
    *   Arguments: `workspace_id` (string, required), `content` (object, required - a JSON object for the active context).
*   **`log_decision`**
    *   Description: Logs an architectural or implementation decision to ConPort.
    *   Arguments: `workspace_id` (string, required), `summary` (string, required), `rationale` (string, optional), `implementation_details` (string, optional).
*   **`get_decisions`**
    *   Description: Retrieves logged decisions from ConPort, optionally limited.
    *   Arguments: `workspace_id` (string, required), `limit` (integer, optional).
*   **`log_progress`**
    *   Description: Logs a progress entry or task status to ConPort.
    *   Arguments: `workspace_id` (string, required), `status` (string, required), `description` (string, required), `parent_id` (integer, optional).
*   **`get_progress`**
    *   Description: Retrieves progress entries from ConPort, optionally filtered.
    *   Arguments: `workspace_id` (string, required), `status_filter` (string, optional), `parent_id_filter` (integer, optional), `limit` (integer, optional).
*   **`log_system_pattern`**
    *   Description: Logs or updates a system/coding pattern used in the project to ConPort.
    *   Arguments: `workspace_id` (string, required), `name` (string, required), `description` (string, optional).
*   **`get_system_patterns`**
    *   Description: Retrieves all logged system patterns from ConPort.
    *   Arguments: `workspace_id` (string, required).
*   **`log_custom_data`**
    *   Description: Stores or updates a custom key-value data entry under a category in ConPort.
    *   Arguments: `workspace_id` (string, required), `category` (string, required), `key` (string, required), `value` (any JSON-serializable type, required).
*   **`get_custom_data`**
    *   Description: Retrieves custom data entries from ConPort, optionally filtered by category/key.
    *   Arguments: `workspace_id` (string, required), `category` (string, optional), `key` (string, optional).
*   **`delete_custom_data`**
    *   Description: Deletes a specific custom data entry from ConPort.
    *   Arguments: `workspace_id` (string, required), `category` (string, required), `key` (string, required).
*   **`export_conport_to_markdown`**
    *   Description: Exports all ConPort data for a workspace to markdown files in a specified output directory (defaults to './conport_export/' relative to the workspace).
    *   Arguments: `workspace_id` (string, required), `output_path` (string, optional - e.g., "my_conport_backup").
*   **`import_markdown_to_conport`**
    *   Description: Imports data from markdown files (typically those generated by `export_conport_to_markdown`) back into the ConPort database for a workspace.
    *   Import Strategy:
        *   Product Context & Active Context: Overwrites existing data.
        *   Decisions, Progress Entries, System Patterns: Adds entries from markdown as new records (may create duplicates if items already exist).
        *   Custom Data: Upserts entries (updates existing category/key pairs, inserts new ones).
        *   Deletions: Does not automatically delete items from the database if they are missing from markdown.
    *   Arguments: `workspace_id` (string, required), `input_path` (string, optional - e.g., "my_conport_backup", defaults to './conport_export/').

## Architecture

The ConPort server is built using Python with FastAPI and utilizes a SQLite database (one per workspace) for persistent storage. Key architectural decisions and schema details were developed during its design phase and are managed internally by the server's database models and MCP tool handlers. For more insight into MCP concepts, refer to the `mcp-reference/` directory.