# Project Brief: Context Portal

## 1. Project Name
Context Portal

## 2. Inspiration / Seed Project
This project evolves from architectural explorations conducted within the "Roo Code Memory Bank" project ([https://github.com/GreatScottyMac/roo-code-memory-bank](https://github.com/GreatScottyMac/roo-code-memory-bank)). It aims to implement the proposed MCP server + database architecture discussed therein.

## 3. Problem Statement
Managing and accessing structured project context (decisions, progress, architecture, domain knowledge, etc.) efficiently and robustly for AI assistants integrated into IDEs presents challenges. The current file-based "Memory Bank" approach, while functional, has limitations regarding complex querying, strict data structure enforcement, AI instruction complexity, and cross-IDE portability.

## 4. Proposed Solution: Context Portal System
Develop a system comprising:
*   **MCP Server (`context_portal_mcp`):** A dedicated server (Python/FastAPI) acting as an API gateway to the project context.
*   **Database Backend:** A structured database (initially SQLite, e.g., `.context_portal/data.sqlite`) storing the context data, with one database file per workspace.
*   **Defined API (MCP Tools):** A set of specific MCP tools (e.g., `log_decision`, `get_active_context`, `log_custom_data`) with clear JSON schemas for AI interaction.
*   **Multi-Workspace Support:** Handle multiple workspaces by requiring a `workspace_id` in all tool calls, used by the server to connect to the correct workspace-specific database.
*   **Dual Deployment Modes:**
    *   Stdio: For direct integration with specific host applications (like Roo Code).
    *   Local HTTP: For cross-IDE compatibility, running as a background service accessible only on `localhost`.

## 5. Key Goals & Features
*   Provide structured, persistent storage for diverse project context types.
*   Offer a robust and well-defined MCP API for AI assistants.
*   Abstract database/storage complexity away from the AI's core instructions.
*   Ensure secure and separate context management for multiple workspaces.
*   Enable usage across different IDEs via the local HTTP mode.
*   Establish a foundation for potential future enhancements like semantic search (vector DB integration).

## 6. Target Users
Primarily AI assistants operating within developer IDEs, enabling them to maintain and leverage deep project context.

## 7. Initial Technology Stack
*   Python (likely 3.9+)
*   FastAPI (for web framework and validation)
*   Pydantic (for data modeling/validation)
*   SQLite

## 8. Initial Task for AI Assistant
1.  Initialize a standard Memory Bank (using the current Markdown file structure) based on this project brief.
2.  Review the architectural proposal (ideally copied from the seed project's `memory-bank/mcp_architecture_proposal.md`).
3.  Begin planning the detailed implementation of the `context_portal_mcp` server and the SQLite database schema based on the proposal.