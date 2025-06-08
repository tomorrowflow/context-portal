"""Initial ConPort database schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-01-08 12:43:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create the initial ConPort database schema."""
    
    # Create product_context table
    op.execute(text("""
        CREATE TABLE product_context (
            id INTEGER PRIMARY KEY DEFAULT 1,
            content TEXT NOT NULL DEFAULT '{}'
        )
    """))
    
    # Insert default row for product_context
    op.execute(text("""
        INSERT INTO product_context (id, content) VALUES (1, '{}')
    """))
    
    # Create active_context table
    op.execute(text("""
        CREATE TABLE active_context (
            id INTEGER PRIMARY KEY DEFAULT 1,
            content TEXT NOT NULL DEFAULT '{}'
        )
    """))
    
    # Insert default row for active_context
    op.execute(text("""
        INSERT INTO active_context (id, content) VALUES (1, '{}')
    """))
    
    # Create decisions table
    op.execute(text("""
        CREATE TABLE decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            summary TEXT NOT NULL,
            rationale TEXT,
            implementation_details TEXT,
            tags TEXT
        )
    """))
    
    # Create progress_entries table
    op.execute(text("""
        CREATE TABLE progress_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL,
            description TEXT NOT NULL,
            parent_id INTEGER,
            FOREIGN KEY (parent_id) REFERENCES progress_entries(id) ON DELETE SET NULL
        )
    """))
    
    # Create system_patterns table
    op.execute(text("""
        CREATE TABLE system_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            tags TEXT
        )
    """))
    
    # Create custom_data table
    op.execute(text("""
        CREATE TABLE custom_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            category TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            UNIQUE(category, key)
        )
    """))
    
    # Create context_links table
    op.execute(text("""
        CREATE TABLE context_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            workspace_id TEXT NOT NULL,
            source_item_type TEXT NOT NULL,
            source_item_id TEXT NOT NULL,
            target_item_type TEXT NOT NULL,
            target_item_id TEXT NOT NULL,
            relationship_type TEXT NOT NULL,
            description TEXT
        )
    """))
    
    # Create product_context_history table
    op.execute(text("""
        CREATE TABLE product_context_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            version INTEGER NOT NULL,
            content TEXT NOT NULL,
            change_source TEXT
        )
    """))
    
    # Create active_context_history table
    op.execute(text("""
        CREATE TABLE active_context_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            version INTEGER NOT NULL,
            content TEXT NOT NULL,
            change_source TEXT
        )
    """))
    
    # Create FTS5 virtual table for decisions
    op.execute(text("""
        CREATE VIRTUAL TABLE decisions_fts USING fts5(
            summary, rationale, implementation_details, tags,
            content='decisions',
            content_rowid='id'
        )
    """))
    
    # Create FTS5 virtual table for custom_data
    op.execute(text("""
        CREATE VIRTUAL TABLE custom_data_fts USING fts5(
            category, key, value_text,
            content='custom_data',
            content_rowid='id'
        )
    """))
    
    # Create triggers to keep FTS tables in sync with main tables
    
    # Triggers for decisions_fts
    op.execute(text("""
        CREATE TRIGGER decisions_fts_insert AFTER INSERT ON decisions BEGIN
            INSERT INTO decisions_fts(rowid, summary, rationale, implementation_details, tags)
            VALUES (new.id, new.summary, new.rationale, new.implementation_details, new.tags);
        END
    """))
    
    op.execute(text("""
        CREATE TRIGGER decisions_fts_delete AFTER DELETE ON decisions BEGIN
            INSERT INTO decisions_fts(decisions_fts, rowid, summary, rationale, implementation_details, tags)
            VALUES ('delete', old.id, old.summary, old.rationale, old.implementation_details, old.tags);
        END
    """))
    
    op.execute(text("""
        CREATE TRIGGER decisions_fts_update AFTER UPDATE ON decisions BEGIN
            INSERT INTO decisions_fts(decisions_fts, rowid, summary, rationale, implementation_details, tags)
            VALUES ('delete', old.id, old.summary, old.rationale, old.implementation_details, old.tags);
            INSERT INTO decisions_fts(rowid, summary, rationale, implementation_details, tags)
            VALUES (new.id, new.summary, new.rationale, new.implementation_details, new.tags);
        END
    """))
    
    # Triggers for custom_data_fts
    op.execute(text("""
        CREATE TRIGGER custom_data_fts_insert AFTER INSERT ON custom_data BEGIN
            INSERT INTO custom_data_fts(rowid, category, key, value_text)
            VALUES (new.id, new.category, new.key, new.value);
        END
    """))
    
    op.execute(text("""
        CREATE TRIGGER custom_data_fts_delete AFTER DELETE ON custom_data BEGIN
            INSERT INTO custom_data_fts(custom_data_fts, rowid, category, key, value_text)
            VALUES ('delete', old.id, old.category, old.key, old.value);
        END
    """))
    
    op.execute(text("""
        CREATE TRIGGER custom_data_fts_update AFTER UPDATE ON custom_data BEGIN
            INSERT INTO custom_data_fts(custom_data_fts, rowid, category, key, value_text)
            VALUES ('delete', old.id, old.category, old.key, old.value);
            INSERT INTO custom_data_fts(rowid, category, key, value_text)
            VALUES (new.id, new.category, new.key, new.value);
        END
    """))


def downgrade():
    """Drop all ConPort database tables."""
    
    # Drop triggers first
    op.execute(text("DROP TRIGGER IF EXISTS custom_data_fts_update"))
    op.execute(text("DROP TRIGGER IF EXISTS custom_data_fts_delete"))
    op.execute(text("DROP TRIGGER IF EXISTS custom_data_fts_insert"))
    op.execute(text("DROP TRIGGER IF EXISTS decisions_fts_update"))
    op.execute(text("DROP TRIGGER IF EXISTS decisions_fts_delete"))
    op.execute(text("DROP TRIGGER IF EXISTS decisions_fts_insert"))
    
    # Drop FTS tables
    op.execute(text("DROP TABLE IF EXISTS custom_data_fts"))
    op.execute(text("DROP TABLE IF EXISTS decisions_fts"))
    
    # Drop main tables
    op.execute(text("DROP TABLE IF EXISTS active_context_history"))
    op.execute(text("DROP TABLE IF EXISTS product_context_history"))
    op.execute(text("DROP TABLE IF EXISTS context_links"))
    op.execute(text("DROP TABLE IF EXISTS custom_data"))
    op.execute(text("DROP TABLE IF EXISTS system_patterns"))
    op.execute(text("DROP TABLE IF EXISTS progress_entries"))
    op.execute(text("DROP TABLE IF EXISTS decisions"))
    op.execute(text("DROP TABLE IF EXISTS active_context"))
    op.execute(text("DROP TABLE IF EXISTS product_context"))