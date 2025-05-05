"""Database interaction logic using sqlite3."""

import sqlite3
import json
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from ..core.config import get_database_path
from ..core.exceptions import DatabaseError, ConfigurationError
from . import models # Import models from the same directory

# --- Connection Handling ---

_connections: Dict[str, sqlite3.Connection] = {}

def get_db_connection(workspace_id: str) -> sqlite3.Connection:
    """Gets or creates a database connection for the given workspace."""
    if workspace_id in _connections:
        return _connections[workspace_id]

    try:
        db_path = get_database_path(workspace_id)
        conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        conn.row_factory = sqlite3.Row # Access columns by name
        _connections[workspace_id] = conn
        initialize_database(conn) # Ensure tables exist
        return conn
    except ConfigurationError as e:
        raise DatabaseError(f"Configuration error getting DB path for {workspace_id}: {e}")
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to connect to database for {workspace_id} at {db_path}: {e}")

def close_db_connection(workspace_id: str):
    """Closes the database connection for the given workspace, if open."""
    if workspace_id in _connections:
        _connections[workspace_id].close()
        del _connections[workspace_id]

def close_all_connections():
    """Closes all active database connections."""
    for workspace_id in list(_connections.keys()):
        close_db_connection(workspace_id)

# --- Database Initialization ---

def initialize_database(conn: sqlite3.Connection):
    """Creates database tables if they don't exist."""
    cursor = conn.cursor()
    try:
        # Product Context (Single Row)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_context (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                content TEXT NOT NULL DEFAULT '{}'
            )
        """)
        # Ensure the single row exists
        cursor.execute("INSERT OR IGNORE INTO product_context (id, content) VALUES (1, '{}')")

        # Active Context (Single Row)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS active_context (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                content TEXT NOT NULL DEFAULT '{}'
            )
        """)
        # Ensure the single row exists
        cursor.execute("INSERT OR IGNORE INTO active_context (id, content) VALUES (1, '{}')")

        # Decisions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP NOT NULL,
                summary TEXT NOT NULL,
                rationale TEXT,
                implementation_details TEXT
            )
        """)

        # Progress Entries
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP NOT NULL,
                status TEXT NOT NULL,
                description TEXT NOT NULL,
                parent_id INTEGER,
                FOREIGN KEY (parent_id) REFERENCES progress_entries(id) ON DELETE SET NULL
            )
        """)

        # System Patterns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT
            )
        """)

        # Custom Data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL, -- Store as JSON string
                UNIQUE(category, key)
            )
        """)

        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise DatabaseError(f"Failed to initialize database tables: {e}")
    finally:
        cursor.close()


# --- CRUD Operations ---

def get_product_context(workspace_id: str) -> models.ProductContext:
    """Retrieves the product context."""
    conn = get_db_connection(workspace_id)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, content FROM product_context WHERE id = 1")
        row = cursor.fetchone()
        if row:
            content_dict = json.loads(row['content'])
            return models.ProductContext(id=row['id'], content=content_dict)
        else:
            # Should not happen if initialized correctly, but handle defensively
            raise DatabaseError("Product context row not found.")
    except (sqlite3.Error, json.JSONDecodeError) as e:
        raise DatabaseError(f"Failed to retrieve product context: {e}")
    finally:
        cursor.close()

def update_product_context(workspace_id: str, context: models.ProductContext) -> None:
    """Updates the product context."""
    conn = get_db_connection(workspace_id)
    cursor = conn.cursor()
    try:
        content_json = json.dumps(context.content)
        cursor.execute("UPDATE product_context SET content = ? WHERE id = 1", (content_json,))
        conn.commit()
        if cursor.rowcount == 0:
             raise DatabaseError("Failed to update product context (row not found or no change).")
    except (sqlite3.Error, TypeError) as e: # TypeError for JSON encoding issues
        conn.rollback()
        raise DatabaseError(f"Failed to update product context: {e}")
    finally:
        cursor.close()
def get_active_context(workspace_id: str) -> models.ActiveContext:
    """Retrieves the active context."""
    conn = get_db_connection(workspace_id)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, content FROM active_context WHERE id = 1")
        row = cursor.fetchone()
        if row:
            content_dict = json.loads(row['content'])
            return models.ActiveContext(id=row['id'], content=content_dict)
        else:
            raise DatabaseError("Active context row not found.")
    except (sqlite3.Error, json.JSONDecodeError) as e:
        raise DatabaseError(f"Failed to retrieve active context: {e}")
    finally:
        cursor.close()

def update_active_context(workspace_id: str, context: models.ActiveContext) -> None:
    """Updates the active context."""
    conn = get_db_connection(workspace_id)
    cursor = conn.cursor()
    try:
        content_json = json.dumps(context.content)
        cursor.execute("UPDATE active_context SET content = ? WHERE id = 1", (content_json,))
        conn.commit()
        if cursor.rowcount == 0:
             raise DatabaseError("Failed to update active context (row not found or no change).")
    except (sqlite3.Error, TypeError) as e:
        conn.rollback()
        raise DatabaseError(f"Failed to update active context: {e}")
    finally:
        cursor.close()

# --- Add more CRUD functions for other models (ActiveContext, Decision, etc.) ---
# Example: log_decision
def log_decision(workspace_id: str, decision_data: models.Decision) -> models.Decision:
    """Logs a new decision."""
    conn = get_db_connection(workspace_id)
    cursor = conn.cursor()
    sql = """
        INSERT INTO decisions (timestamp, summary, rationale, implementation_details)
        VALUES (?, ?, ?, ?)
    """
    params = (
        decision_data.timestamp,
        decision_data.summary,
        decision_data.rationale,
        decision_data.implementation_details
    )
    try:
        cursor.execute(sql, params)
        decision_id = cursor.lastrowid
        conn.commit()
        # Return the full decision object including the new ID
        decision_data.id = decision_id
        return decision_data
    except sqlite3.Error as e:
        conn.rollback()
        raise DatabaseError(f"Failed to log decision: {e}")
    finally:
        cursor.close()

def get_decisions(workspace_id: str, limit: Optional[int] = None) -> List[models.Decision]:
    """Retrieves decisions, optionally limited to the most recent ones."""
    conn = get_db_connection(workspace_id)
    cursor = conn.cursor()
    sql = "SELECT id, timestamp, summary, rationale, implementation_details FROM decisions ORDER BY timestamp DESC"
    params: Tuple = ()
    if limit is not None and limit > 0:
        sql += " LIMIT ?"
        params = (limit,)

    try:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        decisions = [
            models.Decision(
                id=row['id'],
                # Assuming detect_types correctly parses TIMESTAMP columns to datetime
                timestamp=row['timestamp'],
                summary=row['summary'],
                rationale=row['rationale'],
                implementation_details=row['implementation_details']
            ) for row in rows
        ]
        # Return in chronological order (oldest first) if needed, otherwise keep DESC
        # decisions.reverse() # Optional: uncomment to return oldest first
        return decisions
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to retrieve decisions: {e}")
    finally:
        cursor.close()
def log_progress(workspace_id: str, progress_data: models.ProgressEntry) -> models.ProgressEntry:
    """Logs a new progress entry."""
    conn = get_db_connection(workspace_id)
    cursor = conn.cursor()
    sql = """
        INSERT INTO progress_entries (timestamp, status, description, parent_id)
        VALUES (?, ?, ?, ?)
    """
    params = (
        progress_data.timestamp,
        progress_data.status,
        progress_data.description,
        progress_data.parent_id
    )
    try:
        cursor.execute(sql, params)
        progress_id = cursor.lastrowid
        conn.commit()
        progress_data.id = progress_id
        return progress_data
    except sqlite3.Error as e:
        conn.rollback()
        # Consider checking for foreign key constraint errors if parent_id is invalid
        raise DatabaseError(f"Failed to log progress entry: {e}")
    finally:
        cursor.close()
def get_progress(
    workspace_id: str,
    status_filter: Optional[str] = None,
    parent_id_filter: Optional[int] = None,
    limit: Optional[int] = None
) -> List[models.ProgressEntry]:
    """Retrieves progress entries, optionally filtered and limited."""
    conn = get_db_connection(workspace_id)
    cursor = conn.cursor()
    sql = "SELECT id, timestamp, status, description, parent_id FROM progress_entries"
    conditions = []
    params_list = []

    if status_filter:
        conditions.append("status = ?")
        params_list.append(status_filter)
    if parent_id_filter is not None: # Check for None explicitly as 0 could be a valid parent_id
        conditions.append("parent_id = ?")
        params_list.append(parent_id_filter)
    # Add more filters if needed (e.g., date range)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY timestamp DESC" # Default order: newest first

    if limit is not None and limit > 0:
        sql += " LIMIT ?"
        params_list.append(limit)

    params = tuple(params_list)

    try:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        progress_entries = [
            models.ProgressEntry(
                id=row['id'],
                timestamp=row['timestamp'],
                status=row['status'],
                description=row['description'],
                parent_id=row['parent_id']
            ) for row in rows
        ]
        # progress_entries.reverse() # Optional: uncomment to return oldest first
        return progress_entries
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to retrieve progress entries: {e}")
    finally:
        cursor.close()
def log_system_pattern(workspace_id: str, pattern_data: models.SystemPattern) -> models.SystemPattern:
    """Logs or updates a system pattern. Uses INSERT OR REPLACE based on unique name."""
    conn = get_db_connection(workspace_id)
    cursor = conn.cursor()
    # Use INSERT OR REPLACE to handle unique constraint on 'name'
    # This will overwrite the description if the name already exists.
    sql = """
        INSERT OR REPLACE INTO system_patterns (name, description)
        VALUES (?, ?)
    """
    params = (
        pattern_data.name,
        pattern_data.description
    )
    try:
        cursor.execute(sql, params)
        # We might not get the correct lastrowid if it replaced,
        # so we need to query back to get the ID if needed.
        # For now, just commit and assume success or handle error.
        # If returning the model with ID is critical, add a SELECT query here.
        conn.commit()
        # Query back to get the ID (optional, adds overhead)
        cursor.execute("SELECT id FROM system_patterns WHERE name = ?", (pattern_data.name,))
        row = cursor.fetchone()
        if row:
            pattern_data.id = row['id']
        return pattern_data # Return original data, possibly updated with ID
    except sqlite3.Error as e:
        conn.rollback()
        raise DatabaseError(f"Failed to log system pattern '{pattern_data.name}': {e}")
    finally:
        cursor.close()

def get_system_patterns(workspace_id: str) -> List[models.SystemPattern]:
    """Retrieves all system patterns."""
    conn = get_db_connection(workspace_id)
    cursor = conn.cursor()
    sql = "SELECT id, name, description FROM system_patterns ORDER BY name ASC"
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        patterns = [
            models.SystemPattern(
                id=row['id'],
                name=row['name'],
                description=row['description']
            ) for row in rows
        ]
        return patterns
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to retrieve system patterns: {e}")
    finally:
        cursor.close()
def log_custom_data(workspace_id: str, data: models.CustomData) -> models.CustomData:
    """Logs or updates a custom data entry. Uses INSERT OR REPLACE based on unique (category, key)."""
    conn = get_db_connection(workspace_id)
    cursor = conn.cursor()
    sql = """
        INSERT OR REPLACE INTO custom_data (category, key, value)
        VALUES (?, ?, ?)
    """
    try:
        # Ensure value is serialized to JSON string
        value_json = json.dumps(data.value)
        params = (
            data.category,
            data.key,
            value_json
        )
        cursor.execute(sql, params)
        conn.commit()
        # Query back to get ID if needed (similar to log_system_pattern)
        cursor.execute("SELECT id FROM custom_data WHERE category = ? AND key = ?", (data.category, data.key))
        row = cursor.fetchone()
        if row:
            data.id = row['id']
        return data
    except (sqlite3.Error, TypeError) as e: # TypeError for json.dumps
        conn.rollback()
        raise DatabaseError(f"Failed to log custom data for '{data.category}/{data.key}': {e}")
    finally:
        cursor.close()

def get_custom_data(
    workspace_id: str,
    category: Optional[str] = None,
    key: Optional[str] = None
) -> List[models.CustomData]:
    """Retrieves custom data entries, optionally filtered by category and/or key."""
    if key and not category:
        raise ValueError("Cannot filter by key without specifying a category.")

    conn = get_db_connection(workspace_id)
    cursor = conn.cursor()
    sql = "SELECT id, category, key, value FROM custom_data"
    conditions = []
    params_list = []

    if category:
        conditions.append("category = ?")
        params_list.append(category)
    if key: # We already ensured category is present if key is
        conditions.append("key = ?")
        params_list.append(key)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY category ASC, key ASC" # Consistent ordering
    params = tuple(params_list)

    try:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        custom_data_list = []
        for row in rows:
            try:
                # Deserialize value from JSON string
                value_data = json.loads(row['value'])
                custom_data_list.append(
                    models.CustomData(
                        id=row['id'],
                        category=row['category'],
                        key=row['key'],
                        value=value_data
                    )
                )
            except json.JSONDecodeError as e:
                # Log or handle error for specific row if JSON is invalid
                print(f"Warning: Failed to decode JSON for custom_data id={row['id']}: {e}") # Replace with proper logging
                continue # Skip this row
        return custom_data_list
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to retrieve custom data: {e}")
    finally:
        cursor.close()

def delete_custom_data(workspace_id: str, category: str, key: str) -> bool:
    """Deletes a specific custom data entry by category and key. Returns True if deleted, False otherwise."""
    conn = get_db_connection(workspace_id)
    cursor = conn.cursor()
    sql = "DELETE FROM custom_data WHERE category = ? AND key = ?"
    params = (category, key)
    try:
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount > 0 # Return True if one row was deleted
    except sqlite3.Error as e:
        conn.rollback()
        raise DatabaseError(f"Failed to delete custom data for '{category}/{key}': {e}")
    finally:
        cursor.close()
# (All planned CRUD functions implemented)

# --- Cleanup ---
# Consider using a context manager or atexit to ensure connections are closed
import atexit
atexit.register(close_all_connections)