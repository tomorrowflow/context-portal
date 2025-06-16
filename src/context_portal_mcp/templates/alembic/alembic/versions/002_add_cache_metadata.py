"""Add cache metadata and scoring to custom_data table

Revision ID: 002_add_cache_metadata
Revises: 001_initial_schema
Create Date: 2025-01-16 18:33:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = '002_add_cache_metadata'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    """Add metadata and cache_score columns to custom_data table."""
    
    # Add metadata column (JSON type)
    op.execute(text("""
        ALTER TABLE custom_data ADD COLUMN metadata TEXT
    """))
    
    # Add cache_score column (INTEGER type)
    op.execute(text("""
        ALTER TABLE custom_data ADD COLUMN cache_score INTEGER DEFAULT 0
    """))
    
    # Create index for cache hint queries
    op.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_custom_data_cache_hint 
        ON custom_data (JSON_EXTRACT(metadata, '$.cache_hint'))
    """))


def downgrade():
    """Remove metadata and cache_score columns from custom_data table."""
    
    # Drop the index first
    op.execute(text("DROP INDEX IF EXISTS idx_custom_data_cache_hint"))
    
    # Note: SQLite doesn't support DROP COLUMN directly in older versions
    # For a complete downgrade, we would need to recreate the table
    # For now, we'll leave the columns but could implement full table recreation if needed
    
    # If we wanted to fully remove columns (more complex approach):
    # 1. Create new table without the columns
    # 2. Copy data from old table to new table
    # 3. Drop old table
    # 4. Rename new table to original name
    # 5. Recreate triggers and indexes
    
    # For simplicity in this migration, we'll just drop the index
    # The columns will remain but won't be used by the application
    pass