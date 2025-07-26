"""Add cascade delete on student_unit_progress.unit_id

Revision ID: c1c1876d5119
Revises: ec240e08c8e0
Create Date: 2025-07-26 21:07:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c1c1876d5119'
down_revision: Union[str, None] = 'ec240e08c8e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('student_unit_progress_unit_id_fkey', 'student_unit_progress', type_='foreignkey')
    op.create_foreign_key(
        'student_unit_progress_unit_id_fkey',
        'student_unit_progress',
        'units',
        ['unit_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_constraint('student_unit_progress_unit_id_fkey', 'student_unit_progress', type_='foreignkey')
    op.create_foreign_key(
        'student_unit_progress_unit_id_fkey',
        'student_unit_progress',
        'units',
        ['unit_id'],
        ['id']
    )
