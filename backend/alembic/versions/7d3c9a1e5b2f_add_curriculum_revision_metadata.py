"""add curriculum revision metadata

Revision ID: 7d3c9a1e5b2f
Revises: 1f2e3d4c5b6a
Create Date: 2026-05-12 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7d3c9a1e5b2f"
down_revision: Union[str, None] = "1f2e3d4c5b6a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _add_revision_columns(table_name: str) -> None:
    op.add_column(
        table_name,
        sa.Column("revision_number", sa.Integer(), nullable=False, server_default=sa.text("1")),
    )
    op.add_column(table_name, sa.Column("revision_label", sa.String(), nullable=True))
    op.add_column(
        table_name,
        sa.Column("revision_status", sa.String(), nullable=False, server_default="current"),
    )
    op.add_column(
        table_name,
        sa.Column("revision_metadata", sa.JSON(), nullable=True, server_default=sa.text("'{}'::json")),
    )
    op.add_column(table_name, sa.Column("published_at", sa.DateTime(), nullable=True))
    op.add_column(table_name, sa.Column("deprecated_at", sa.DateTime(), nullable=True))


def _drop_revision_columns(table_name: str) -> None:
    op.drop_column(table_name, "deprecated_at")
    op.drop_column(table_name, "published_at")
    op.drop_column(table_name, "revision_metadata")
    op.drop_column(table_name, "revision_status")
    op.drop_column(table_name, "revision_label")
    op.drop_column(table_name, "revision_number")


def upgrade() -> None:
    for table_name in ("courses", "units", "lessons", "assessments"):
        _add_revision_columns(table_name)


def downgrade() -> None:
    for table_name in ("assessments", "lessons", "units", "courses"):
        _drop_revision_columns(table_name)
