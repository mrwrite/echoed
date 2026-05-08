"""add assessment backbone metadata

Revision ID: 6a2c3f4d5e6b
Revises: b7f9c3e12a6d
Create Date: 2026-05-08 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6a2c3f4d5e6b"
down_revision: Union[str, None] = "b7f9c3e12a6d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("assessments", sa.Column("unit_id", sa.UUID(), nullable=True))
    op.add_column("assessments", sa.Column("assessment_scope", sa.String(), nullable=True))
    op.add_column("assessments", sa.Column("assessment_state", sa.String(), nullable=True))
    op.add_column("assessments", sa.Column("availability_state", sa.String(), nullable=True))
    op.add_column("assessments", sa.Column("policy_metadata", sa.JSON(), nullable=True))
    op.add_column("assessments", sa.Column("lifecycle_metadata", sa.JSON(), nullable=True))

    op.create_foreign_key(
        "fk_assessments_unit_id_units",
        "assessments",
        "units",
        ["unit_id"],
        ["id"],
    )
    op.create_index(op.f("ix_assessments_unit_id"), "assessments", ["unit_id"], unique=False)

    op.execute(
        sa.text(
            """
            UPDATE assessments
            SET assessment_scope = CASE
                WHEN unit_id IS NOT NULL THEN 'unit'
                WHEN lesson_id IS NOT NULL THEN 'lesson'
                WHEN course_id IS NOT NULL THEN 'course'
                WHEN program_id IS NOT NULL THEN 'program'
                ELSE assessment_scope
            END,
            assessment_state = COALESCE(assessment_state, 'published'),
            availability_state = COALESCE(availability_state, 'available')
            """
        )
    )


def downgrade() -> None:
    op.drop_constraint("fk_assessments_unit_id_units", "assessments", type_="foreignkey")
    op.drop_index(op.f("ix_assessments_unit_id"), table_name="assessments")
    op.drop_column("assessments", "lifecycle_metadata")
    op.drop_column("assessments", "policy_metadata")
    op.drop_column("assessments", "availability_state")
    op.drop_column("assessments", "assessment_state")
    op.drop_column("assessments", "assessment_scope")
    op.drop_column("assessments", "unit_id")
