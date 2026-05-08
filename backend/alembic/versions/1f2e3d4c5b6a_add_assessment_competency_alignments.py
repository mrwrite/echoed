"""add assessment competency alignments

Revision ID: 1f2e3d4c5b6a
Revises: 8f3c1a9b2d47
Create Date: 2026-05-08 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1f2e3d4c5b6a"
down_revision: Union[str, None] = "8f3c1a9b2d47"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "assessment_competency_alignments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("assessment_id", sa.UUID(), nullable=False),
        sa.Column("question_id", sa.UUID(), nullable=True),
        sa.Column("objective_key", sa.String(), nullable=False),
        sa.Column("objective_title", sa.String(), nullable=True),
        sa.Column("objective_type", sa.String(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False, server_default=sa.text("1")),
        sa.Column("mastery_threshold", sa.Float(), nullable=False, server_default=sa.text("80")),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"]),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_assessment_competency_alignments_id"), "assessment_competency_alignments", ["id"], unique=False)
    op.create_index(op.f("ix_assessment_competency_alignments_assessment_id"), "assessment_competency_alignments", ["assessment_id"], unique=False)
    op.create_index(op.f("ix_assessment_competency_alignments_question_id"), "assessment_competency_alignments", ["question_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_assessment_competency_alignments_question_id"), table_name="assessment_competency_alignments")
    op.drop_index(op.f("ix_assessment_competency_alignments_assessment_id"), table_name="assessment_competency_alignments")
    op.drop_index(op.f("ix_assessment_competency_alignments_id"), table_name="assessment_competency_alignments")
    op.drop_table("assessment_competency_alignments")
