"""Add progress status enums

Revision ID: 46a1d197f625
Revises: 44552f7ef700
Create Date: 2025-06-22 09:58:58.198028

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import enum


# revision identifiers, used by Alembic.
revision = '46a1d197f625'
down_revision = '44552f7ef700'
branch_labels = None
depends_on = None


# Re-declare enums (must match your `enum.py`)
class ProgressStatus(enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    DELIVERED = "DELIVERED"


def upgrade():
    # Create ENUM types
    progress_enum = sa.Enum(ProgressStatus, name="progress_status_enum")
    segment_enum = sa.Enum(ProgressStatus, name="segment_status_enum")
    progress_enum.create(op.get_bind(), checkfirst=True)
    segment_enum.create(op.get_bind(), checkfirst=True)

    # Normalize old string values to enum format BEFORE type change
    conn = op.get_bind()
    conn.execute(
        sa.text("""
            UPDATE student_unit_progress
            SET status = UPPER(status)
            WHERE status IS NOT NULL
        """)
    )
    conn.execute(
        sa.text("""
            UPDATE segment_progress
            SET status = UPPER(status)
            WHERE status IS NOT NULL
        """)
    )

    # Now apply the type change
    op.alter_column(
        'student_unit_progress',
        'status',
        type_=progress_enum,
        existing_type=sa.String(),
        postgresql_using="status::progress_status_enum",
        existing_nullable=True,
    )
    op.alter_column(
        'segment_progress',
        'status',
        type_=segment_enum,
        existing_type=sa.String(),
        postgresql_using="status::segment_status_enum",
        existing_nullable=True,
    )




def downgrade():
    # Revert columns back to String
    op.alter_column('segment_progress', 'status',
        type_=sa.String(),
        existing_type=sa.Enum(ProgressStatus, name="segment_status_enum"),
        existing_nullable=True
    )

    op.alter_column('student_unit_progress', 'status',
        type_=sa.String(),
        existing_type=sa.Enum(ProgressStatus, name="progress_status_enum"),
        existing_nullable=True
    )

    # Drop enums
    segment_enum = sa.Enum(ProgressStatus, name="segment_status_enum")
    progress_enum = sa.Enum(ProgressStatus, name="progress_status_enum")
    segment_enum.drop(op.get_bind(), checkfirst=True)
    progress_enum.drop(op.get_bind(), checkfirst=True)
