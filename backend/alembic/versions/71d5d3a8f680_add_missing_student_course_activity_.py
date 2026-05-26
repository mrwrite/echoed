"""add missing student course activity columns

Revision ID: 71d5d3a8f680
Revises: c4a6d9f2b8e1
Create Date: 2026-05-16 18:15:07.002058

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '71d5d3a8f680'
down_revision: Union[str, None] = 'c4a6d9f2b8e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column("student_courses", sa.Column("last_activity_at", sa.DateTime(), nullable=True))
    op.add_column("student_courses", sa.Column("completed_at", sa.DateTime(), nullable=True))
    op.add_column("segment_progress", sa.Column("started_at", sa.DateTime(), nullable=True))
    op.add_column("segment_progress", sa.Column("completed_at", sa.DateTime(), nullable=True))
    op.add_column("student_unit_progress", sa.Column("started_at", sa.DateTime(), nullable=True))
    op.add_column("student_unit_progress", sa.Column("completed_at", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("student_unit_progress", "completed_at")
    op.drop_column("student_unit_progress", "started_at")
    op.drop_column("segment_progress", "completed_at")
    op.drop_column("segment_progress", "started_at")
    op.drop_column("student_courses", "completed_at")
    op.drop_column("student_courses", "last_activity_at")
