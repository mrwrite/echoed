"""merge heads: orgs + latest

Revision ID: e9794a72f032
Revises: 10f6c2f8d567, 2024_10_01_orgs
Create Date: 2026-02-07 00:02:32.390462

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e9794a72f032'
down_revision: Union[str, None] = ('10f6c2f8d567', '2024_10_01_orgs')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
