"""Add cascade delete to segment_progress.lesson_id

Revision ID: ec240e08c8e0
Revises: 46a1d197f625
Create Date: 2025-07-26 20:43:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'ec240e08c8e0'
down_revision: Union[str, None] = '46a1d197f625'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('segment_progress_lesson_id_fkey', 'segment_progress', type_='foreignkey')
    op.create_foreign_key(
        'segment_progress_lesson_id_fkey',
        'segment_progress', 'lessons',
        ['lesson_id'], ['id'], ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_constraint('segment_progress_lesson_id_fkey', 'segment_progress', type_='foreignkey')
    op.create_foreign_key(
        'segment_progress_lesson_id_fkey',
        'segment_progress', 'lessons',
        ['lesson_id'], ['id']
    )
