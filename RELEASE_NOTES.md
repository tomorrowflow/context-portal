## Version 0.2.6 - Bug Fix Release

This release addresses a critical issue with Alembic database migrations that could occur when initializing ConPort in environments where a `context.db` file already existed, but without proper Alembic version tracking.

**Key Fix:**
- Modified the initial Alembic migration script (`068b7234d6a7_initial_database_schema.py`) to use `CREATE TABLE IF NOT EXISTS` for the `product_context` and `active_context` tables. This prevents `sqlite3.OperationalError` when the tables are already present, ensuring smoother initialization and operation of the ConPort server.

**Impact:**
This fix improves the robustness of ConPort's database initialization process, particularly in scenarios involving partial or pre-existing database setups.