# Context Portal MCP (ConPort)

A database-backed Model Context Protocol (MCP) server for managing structured project context, designed to be used by AI assistants and developer tools within IDEs and other interfaces.

## Overview

This project is the **Context Portal MCP server (ConPort)**. ConPort provides a robu nst and structured way for AI assistants to store, retrieve, and manage various types of project context (e.g., product goals, active tasks, decisions, progress, architectural patterns, custom data) via a dedicated MCP server.

It can replace older file-based context management systems by offering a more reliable and queryable database backend (SQLite per workspace). ConPort is designed to be a generic context backend, compatible with various IDEs and client interfaces that support MCP.

Key features include:
*   Structured context storage using SQLite (one DB per workspace).
*   MCP server (`context_portal_mcp`) built with Python/FastAPI.
*   Defined MCP tools for interaction (e.g., `log_decision`, `get_active_context`).
*   Multi-workspace support via `workspace_id`.
*   Deployment mode: Stdio.

## Prerequisites

Before you begin, ensure you have the following installed:

*   **Git:** For cloning the repository.
    *   [Download and Install Git](https://git-scm.com/downloads)
*   **Python:** Version 3.8 or higher is recommended.
    *   [Download Python](https://www.python.org/downloads/)
    *   Ensure Python is added to your system's PATH during installation (especially on Windows).
*   **uv:** (Recommended) A fast Python environment and package manager. Using `uv` simplifies virtual environment creation and dependency installation.
    *   [Install uv](https://github.com/astral-sh/uv#installation)
    *   If you prefer not to use `uv`, you can use standard Python `venv` and `pip`.

## Installation from Git Repository

These instructions guide you through setting up ConPort by cloning its Git repository and installing dependencies. It's highly recommended to use a virtual environment to manage project dependencies and avoid conflicts with system Python packages.

1.  **Clone the Repository:**
    Open your terminal or command prompt and run the following command, replacing `context-portal.git` with the actual repository URL if necessary (e.g., if you've forked it).
    ```bash
    git clone https://github.com/context-portal/context-portal.git
    cd context-portal
    ```

2.  **Create and Activate a Virtual Environment:**

    Using a virtual environment isolates the project's Python dependencies from your system's Python installation.

    *   **Using `uv` (recommended):**

        ```bash
        uv venv
        ```
        *   **Activate the environment:**
            *   **Linux/macOS:**
                ```bash
                source .venv/bin/activate
                ```
            *   **Windows Command Prompt:**
                ```cmd
                .venv\Scripts\activate.bat
                ```
            *   **Windows PowerShell:**
                ```powershell
                .venv\Scripts\Activate.ps1
                ```

    *   **Using standard `venv`:**

        ```bash
        python3 -m venv .venv  # On some systems, use 'python -m venv .venv'
        ```
        *   **Activate the environment:**
            *   **Linux/macOS:**
                ```bash
                source .venv/bin/activate
                ```
            *   **Windows Command Prompt:**
                ```cmd
                .venv\Scripts\activate.bat
                ```
            *   **Windows PowerShell:**
                ```powershell
                .venv\Scripts\Activate.ps1
                ```

3.  **Install Dependencies:**

    With your virtual environment activated, install the project dependencies listed in `requirements.txt`.

    *   **Using `uv` (recommended):**
        ```bash
        uv pip install -r requirements.txt
        ```
    *   **Using standard `pip` (if you used `venv`):**
        ```bash
        pip install -r requirements.txt
        ```

4.  **Verify Installation (Optional):**

    You can check if the main script is accessible and prints help information. Ensure your virtual environment is activated.

    *   **If you used `uv`:**
        ```bash
        uv run python src/context_portal_mcp/main.py --help
        ```
    *   **If you used standard `venv`:**
        ```bash
        python src/context_portal_mcp/main.py --help
        ```
    This command should output the command-line help for the ConPort server.

## Running the ConPort Server

The ConPort server is primarily designed to be run in STDIO mode for IDE integration.

### STDIO Mode (Recommended for IDE Integration)

This mode is ideal for tight integration with an IDE (like VS Code or Roo Code), where the IDE spawns and manages the server process for the current workspace.

*   **Command Structure:**

    ```bash
    <python_runner> src/context_portal_mcp/main.py --mode stdio --workspace_id "/actual/path/to/your/project_workspace"
    ```
    *   Replace `<python_runner>` with:
        *   `uv run python` if you installed dependencies using `uv`.
        *   `python` if you installed dependencies using standard `venv` and `pip` (ensure your virtual environment is activated).
    *   Replace `"/actual/path/to/your/project_workspace"` with the absolute path to the root of the workspace whose context you want ConPort to manage. The IDE typically provides this path dynamically (e.g., via a variable like `${workspaceFolder}`).
    *   ConPort will create/use a database file at `your_project_workspace/.context_portal/data.sqlite`.

## Client Configuration

MCP clients (like IDE extensions or other tools) need to be configured to connect to a running ConPort instance.

### For STDIO Mode (e.g., in a workspace `.vscode/mcp.json` or the IDE's user-level MCP settings)

**Note:** Whether you configure ConPort in a workspace-specific file or your IDE's user-level (global) MCP settings, the `command`, `args` (specifically the path to `main.py`), and `cwd` parameters in the configuration below MUST always point to the location where YOU cloned the `context-portal` repository.
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
*   **Important:**
    *   Replace `/path/to/your/context-portal-mcp-repo` in both the `args` (for `main.py`) and the `cwd` parameter with the **absolute path** to the directory where you cloned this `context-portal` repository.
    *   For example, if you cloned it into `/home/user/projects/context-portal`, then the `main.py` path would be `/home/user/projects/context-portal/src/context_portal_mcp/main.py` and `cwd` would be `/home/user/projects/context-portal`.
*   `${workspaceFolder}` is a common IDE variable (like in VS Code or Roo Code) that represents the absolute path to the root of the project workspace the user currently has open. ConPort will manage context for *this* workspace.

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