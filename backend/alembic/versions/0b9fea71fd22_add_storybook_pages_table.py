"""Create storybook_pages table

Revision ID: 0b9fea71fd22
Revises: c1c1876d5119
Create Date: 2025-07-29 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '0b9fea71fd22'
down_revision: Union[str, None] = 'c1c1876d5119'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'storybook_pages',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('activity_id', sa.UUID(), nullable=False),
        sa.Column('image_url', sa.String(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['activity_id'], ['activities.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_storybook_pages_id'), 'storybook_pages', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_storybook_pages_id'), table_name='storybook_pages')
    op.drop_table('storybook_pages')
