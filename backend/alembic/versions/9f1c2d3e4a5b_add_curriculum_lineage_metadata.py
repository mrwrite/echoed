"""add curriculum lineage metadata

Revision ID: 9f1c2d3e4a5b
Revises: 7d3c9a1e5b2f
Create Date: 2026-05-13 08:45:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "9f1c2d3e4a5b"
down_revision = "7d3c9a1e5b2f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table_name in ("courses", "units", "lessons", "assessments"):
        op.add_column(
            table_name,
            sa.Column("previous_revision_id", postgresql.UUID(as_uuid=True), nullable=True),
        )
        op.add_column(
            table_name,
            sa.Column("superseded_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        )
        op.add_column(
            table_name,
            sa.Column("lineage_status", sa.String(), nullable=False, server_default="standalone"),
        )
        op.add_column(
            table_name,
            sa.Column("lineage_metadata", sa.JSON(), nullable=True, server_default=sa.text("'{}'::json")),
        )
        op.alter_column(table_name, "lineage_status", server_default=None)
        op.alter_column(table_name, "lineage_metadata", server_default=None)


def downgrade() -> None:
    for table_name in ("assessments", "lessons", "units", "courses"):
        op.drop_column(table_name, "lineage_metadata")
        op.drop_column(table_name, "lineage_status")
        op.drop_column(table_name, "superseded_by_id")
        op.drop_column(table_name, "previous_revision_id")
