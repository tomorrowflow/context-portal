# Context Portal MCP Release Notes

<br>

## Version 0.2.9 - Path Escaping Hotfix

This release addresses a critical bug that caused MCP connection failures on Windows due to improper path escaping.

**Key Fix:**

- **JSON Escape Character Fix:** Modified `src/context_portal_mcp/db/database.py` to use `.as_posix()` when constructing file paths for Alembic. This ensures that all paths use forward slashes, preventing `SyntaxError: Bad escaped character in JSON` errors when the server communicates with the client on Windows.

**Impact:**

This is a critical fix for Windows users, ensuring the ConPort MCP server can start and run reliably.

<br>

## Version 0.2.8 - Alembic, Encoding, and Usability Enhancements

This release introduces several key improvements, including a fix for Alembic migrations, enhanced UTF-8 encoding for file operations, and a streamlined installation process.

**Key Fixes & Enhancements:**

- **Alembic Migration Fix:** Resolved a bug that caused import failures for `system_patterns.md` due to a missing `timestamp` column in the database schema. A new Alembic migration script has been added to correctly add this column, ensuring data integrity and successful imports.
- **UTF-8 Encoding:** All file read/write operations during data import and export now explicitly use `encoding="utf-8"`. This prevents encoding errors and ensures cross-platform compatibility.
- **Streamlined Installation:** The `README.md` has been updated to feature `uvx` as the primary and recommended method for running the ConPort server. This simplifies the setup process for new users. A special thanks to contributor [elasticdotventures](https://github.com/elasticdotventures) for their work on the `uvx` configuration.
- **Automated Alembic Provisioning:** The ConPort server now automatically ensures that the necessary `alembic.ini` and `alembic/` directory are present in the workspace root at startup, copying them from internal templates if they are missing.
- **Runtime Error Fix:** Corrected an `IndentationError` in `main.py` that occurred during server startup.

**Impact:**

This release improves the robustness and reliability of ConPort's database migrations and data handling. The updated documentation and automated Alembic provisioning make the server easier to set up and use, while the encoding fix ensures that data is handled consistently across different environments.

<br>

## Version 0.2.6 - Bug Fix Release

This release addresses a critical issue with Alembic database migrations that could occur when initializing ConPort in environments where a `context.db` file already existed, but without proper Alembic version tracking.

**Key Fix:**
- Modified the initial Alembic migration script (`068b7234d6a7_initial_database_schema.py`) to use `CREATE TABLE IF NOT EXISTS` for the `product_context` and `active_context` tables. This prevents `sqlite3.OperationalError` when the tables are already present, ensuring smoother initialization and operation of the ConPort server.

**Impact:**
This fix improves the robustness of ConPort's database initialization process, particularly in scenarios involving partial or pre-existing database setups.

<br>

## v0.2.5 Release Notes

This release focuses on enhancing deployment flexibility and improving the PyPI package.

### Key Updates:

*   **Official Docker Image:** Context Portal MCP is now available as an official Docker image on Docker Hub (`greatscottymac/context-portal-mcp`). This provides a streamlined way to deploy and run ConPort without needing to manage Python environments directly.
    *   Updated [`README.md`](README.md) with comprehensive instructions on how to pull and run the Docker image, including direct `docker run` commands and recommended MCP client configurations for seamless IDE integration.
    *   Added a new section to [`CONTRIBUTING.md`](CONTRIBUTING.md) detailing the process for building and publishing Docker images for contributors.
    
*   **PyPI Package Improvements:**
    *   The `context-portal-mcp` PyPI package has been updated to version `0.2.5`.
    *   Dependency conflicts, specifically related to `sentence-transformers` and `chromadb` which caused issues in certain environments (like Alpine-based Docker images), have been resolved by removing these non-core dependencies from the `requirements.txt`. This results in a leaner and more compatible PyPI distribution.

### How to Update:

*   **Docker Users:** Pull the latest image: `docker pull greatscottymac/context-portal-mcp:latest`
*   **PyPI Users:** Upgrade your installation: `pip install --upgrade context-portal-mcp`

We recommend all users update to this version for improved deployment options and stability.

<br>

## ConPort v0.2.4 Update Notes

This release focuses on significant stability improvements, particularly around database management and migration, alongside enhanced data import capabilities.

### Key Changes and Bug Fixes:

#### 1. Robust Database Initialization and Migration (Alembic)
*   **Problem:** Persistent `alembic` migration failures, including `"No 'script_location' key found in configuration"` and `Can't locate revision` errors, which led to an inconsistent database state.
*   **Solution:**
    *   Refactored `src/context_portal_mcp/db/database.py` to ensure robust Alembic pathing and programmatic configuration of `script_location` and `sqlalchemy.url`.
    *   Introduced `ensure_alembic_files_exist` to reliably provision `alembic.ini` and the `alembic/` directory in the workspace, copying them from internal templates if missing. This ensures a consistent and correct Alembic environment for each workspace.
    *   Integrated this provisioning into `src/context_portal_mcp/main.py`'s `stdio` mode startup, guaranteeing that the Alembic environment is set up on server launch.
    *   Implemented a clean migration strategy that involves deleting the `context.db`, `alembic.ini`, and the `alembic/` directory to force a fresh, consistent migration when critical revision errors occur.

#### 2. Resolved Database Operation Errors
*   **Problem:** Recurrent `NameError: name 'cursor' is not defined` exceptions during database operations (e.g., `get_product_context`, `log_custom_data`), which prevented proper data interaction.
*   **Solution:** Modified all relevant database functions in `src/context_portal_mcp/db/database.py` to correctly initialize `cursor = None` and ensure `cursor.close()` is only called if `cursor` was successfully assigned, making database interactions more robust.

#### 3. Timestamp Column Schema Consistency
*   **Problem:** Inconsistent schema for `timestamp` columns in `system_patterns` and `custom_data` tables, leading to import failures and `AttributeError` exceptions.
*   **Solution:** Verified and resolved discrepancies in the database schema, ensuring that `timestamp` columns are correctly present and accessible in both `system_patterns` and `custom_data` tables. This involved identifying and removing redundant migration attempts.

#### 4. Enhanced Data Import Capabilities
*   **Problem:** Need to import existing ConPort data from various backup sources into a newly provisioned or migrated database.
*   **Solution:** Successfully implemented a two-phase data import strategy using `import_markdown_to_conport`, allowing for the consolidation of project data from multiple markdown export sources (e.g., `conport-export/` and `conport_migration_test_backup/`). This ensures that existing project context, decisions, progress, and custom data can be seamlessly integrated.

#### 5. General Stability and Reliability
*   Addressed various minor issues including `IndentationError`, `SyntaxError`, `pip.exe` missing from `uv venv`, incorrect `package-data` in `pyproject.toml`, ChromaDB `ValueError` for list metadata, and log file location issues.
*   Improved overall server startup and database connection handling.

### Upgrade Notes:
*   Users upgrading from previous versions are recommended to ensure their `alembic.ini` and `alembic/` directories in the workspace are correctly provisioned by starting the ConPort server. If issues persist, consider deleting `context.db`, `alembic.ini`, and the `alembic/` directory in your workspace to allow for a clean re-provisioning and migration.
<br>

## Context Portal MCP v0.2.3 Update Notes

This release focuses on improving the stability, reliability, and user experience of Context Portal MCP, particularly concerning database migrations and documentation.

**Key Changes and Improvements:**

*   **Enhanced Database Migration Reliability:**
    *   Resolved `AttributeError` for `timestamp` fields in `CustomData` and `SystemPattern` models, ensuring smoother data handling.
    *   Corrected Alembic `script_location` in `alembic.ini` and ensured all necessary Alembic configuration files are correctly bundled within the PyPI package. This significantly improves the robustness of database migrations for new installations and updates.
    *   Verified successful data import and custom data handling after fresh database migrations.
*   **Updated and Clarified Documentation:**
    *   Revised [`README.md`](README.md) and [`v0.2.3_UPDATE_GUIDE.md`](v0.2.3_UPDATE_GUIDE.md) to provide the most accurate and up-to-date instructions.
    *   Updated `uv` commands in the documentation to `uv pip install` and `uv pip uninstall` for correct usage.
    *   Clarified Alembic setup, `workspace_id` usage, and requirements for custom data values to be valid JSON.

We recommend all users update to `v0.2.3` for these critical improvements. Please refer to the [v0.2.3_UPDATE_GUIDE.md](v0.2.3_UPDATE_GUIDE.md) for detailed update instructions.

<br>

## v0.2.2 - Patch Release (2025-05-30)

This patch release addresses critical packaging issues related to Alembic, ensuring a smoother installation and migration experience for users.

### Fixes & Improvements:
- **Alembic Configuration Bundling:** Corrected `pyproject.toml` to properly include the `alembic/` directory and `alembic.ini` in the PyPI package. This resolves issues where Alembic migrations would fail for users installing via PyPI due to missing configuration files.
- **Documentation Updates:** Includes the latest comprehensive `README.md` and `v0.2.0_UPDATE_GUIDE.md` with detailed instructions for `uv` and `pip` users, pre-upgrade cleanup, and manual migration steps.

<br>

## v0.2.1 - Patch Release (2025-05-30)

This patch release is primarily focused on providing updated and clearer documentation for the `v0.2.0` upgrade path.

### Improvements:
- **Comprehensive Update Guide:** Introduced `v0.2.0_UPDATE_GUIDE.md` with detailed instructions for upgrading from `v0.1.x` to `v0.2.0`, including manual data migration steps and troubleshooting.
- **README.md Enhancements:** Updated `README.md` to include `uv` commands as primary options and removed redundant database migration notes.

<br>

## v0.2.0 - Major Update (2025-05-30)

This release introduces significant architectural improvements, critical bug fixes, and enhanced context management capabilities.

### New Features:
- **Expanded Active Context Schema:** The active context (`get_active_context`, `update_active_context`) now supports more detailed and structured information, including `current_focus` and `open_issues`, providing richer context for AI assistants.

### Fixes & Improvements:
- **Critical Connection Error Fix:** Resolved a critical connection error in `main.py` that could prevent the server from starting or maintaining a stable connection.
- **Improved Logging:** Enhanced server-side logging for better visibility into operations and easier debugging.
- **ChromaDB Tag Handling:** Fixed a `ValueError` where list-type tags were incorrectly passed to ChromaDB's `upsert` function, ensuring robust vector store metadata handling.
- **`CustomData` Timestamp:** Added a `timestamp` field to the `CustomData` model, enabling better tracking and querying of custom data entries.
- **Initial Alembic Integration:** Introduced Alembic for automated database schema management. While the initial integration in this version might require manual steps for older databases, it lays the groundwork for seamless future upgrades.

<br>

## v0.1.9 - Initial Alembic Integration (2025-05-30)

This release marks the initial integration of Alembic for database schema management.

### New Features:
- **Alembic Database Migrations:** ConPort now uses Alembic to manage its `context.db` schema. This enables automated database upgrades when updating the `context-portal-mcp` package, designed to preserve existing data.

### Important Notes:
- For users upgrading from versions prior to `v0.1.9`, a manual data migration (export, delete `context.db`, import) might be necessary due to significant schema changes. Refer to the `UPDATE_GUIDE.md` for detailed instructions.

<br>

## v0.1.8 - Enhanced Logging, Critical Fixes, and Improved Context Handling

This release brings significant improvements to the ConPort MCP server, focusing on enhanced observability, critical bug fixes, and more robust context management. Thanks @devxpain !!

### Key Changes:

*   **Fixed Vector Store Metadata Handling:** Resolved a `ValueError` that occurred when upserting embeddings with list-type tags (e.g., decision tags). Tags are now correctly converted to a scalar format before being sent to the vector store, ensuring proper semantic search functionality.
*   **New Logging Options:** Introduced `--log-file` and `--log-level` command-line arguments to `main.py`, allowing users to configure log output to a file with rotation and control the verbosity of server logs. This greatly enhances debugging and monitoring capabilities.
*   **Critical Connection Error Fix:** Removed a problematic internal assertion in `main.py` that was causing frequent "Connection closed" errors during development, particularly when the server attempted to create its database within its own installation directory. This improves server stability and developer experience.
*   **Updated Documentation:** Revised `README.md` to include consistent and accurate configuration examples for the new logging options across all installation types (PyPI and Git repository, including Windows examples).

### Changes made after v0.1.7:

*   **Vector Store Metadata Fix:** Specifically, the `ValueError` related to list-type tags in embeddings was addressed in `src/context_portal_mcp/handlers/mcp_handlers.py`.
*   **Integration of PR #14:** The new logging features and the critical connection error fix from PR #14 were merged into `main.py`.
*   **README.md Consistency:** The `README.md` was updated to ensure the Windows configuration examples for logging were consistent with other platforms.

<br>

## v0.1.7

Fixed the `export_conport_to_markdown` tool so that it includes `current_focus` and `open_issues` fields, along with the existing `current_task`.

<br>

## v0.1.6

Fixed incorrect script entry point in pyproject.toml, updated to:
conport-mcp = "context_portal_mcp.main:cli_entry_point"

Corrected the license reference in pyproject.toml to Apache 2.0

<br>

## v0.1.4

Added PyPi installation option

<br>

## v0.1.3

**Release Notes Summary: Semantic Search & Enhanced Data Intelligence**

This version introduces a powerful semantic search capability to ConPort, along with a more intelligent data backend:

*   **New Semantic Search Tool (`semantic_search_conport`)**:
    *   Users can now search for ConPort items (Decisions, Progress, System Patterns, Custom Data, etc.) based on the semantic meaning of their query text, going beyond simple keyword matching.
    *   Supports advanced filtering by item type, tags (match all or any), and custom data categories to refine search results.

*   **Automatic Embedding Generation**:
    *   Key ConPort items (Decisions, Progress Entries, System Patterns, and text-based Custom Data) now automatically have embeddings generated and stored when they are logged.
    *   This powers the semantic search and enables future AI-driven insights.
    *   Utilizes the `all-MiniLM-L6-v2` model for generating embeddings, ensuring consistency.

*   **Integrated Vector Store (ChromaDB)**:
    *   Embeddings are stored in a local ChromaDB vector database, managed per workspace within the `.conport_vector_data` directory.
    *   The system now explicitly configures ChromaDB to use the project's defined embedding model, enhancing consistency and reliability.

*   **Embedding Lifecycle Management**:
    *   Embeddings are now automatically removed from the vector store when their corresponding items (currently Decisions and System Patterns) are deleted from ConPort, keeping the search index synchronized.

These updates significantly enhance the ability to find relevant information within your ConPort workspace and lay the groundwork for more advanced contextual understanding features.

<br>

v0.1.2

ConPort custom instructions refactored with better YAML nesting.

<br>

v0.1.1

Added logic to handle prompt caching when a compatible LLM is being used. 

<br>

v0.1.0-beta

Introducing Context Portal MCP (ConPort), a database-backed Model Context Protocol (MCP) server for managing structured project context, designed to be used by AI assistants and developer tools within IDEs and other interfaces.