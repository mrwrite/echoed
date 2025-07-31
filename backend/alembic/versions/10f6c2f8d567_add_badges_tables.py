"""Add badges and student_badges tables

Revision ID: 10f6c2f8d567
Revises: 0b9fea71fd22
Create Date: 2025-08-01 00:00:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '10f6c2f8d567'
down_revision: Union[str, None] = '0b9fea71fd22'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'badges',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_badges_id'), 'badges', ['id'], unique=False)

    op.create_table(
        'student_badges',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('student_id', sa.UUID(), nullable=False),
        sa.Column('badge_id', sa.UUID(), nullable=False),
        sa.Column('awarded_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['users.id']),
        sa.ForeignKeyConstraint(['badge_id'], ['badges.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_student_badges_id'), 'student_badges', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_student_badges_id'), table_name='student_badges')
    op.drop_table('student_badges')
    op.drop_index(op.f('ix_badges_id'), table_name='badges')
    op.drop_table('badges')
