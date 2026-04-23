"""add lesson quality fields and sources

Revision ID: c4a6d9f2b8e1
Revises: b7f9c3e12a6d
Create Date: 2026-04-23 00:00:01
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c4a6d9f2b8e1"
down_revision: Union[str, None] = "b7f9c3e12a6d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("lessons", sa.Column("key_concepts", sa.JSON(), nullable=True))
    op.add_column("lessons", sa.Column("teacher_notes", sa.Text(), nullable=True))
    op.add_column("lessons", sa.Column("discussion_questions", sa.JSON(), nullable=True))
    op.add_column("lessons", sa.Column("hook", sa.Text(), nullable=True))
    op.add_column("lessons", sa.Column("content", sa.Text(), nullable=True))
    op.add_column("lessons", sa.Column("guided_practice", sa.Text(), nullable=True))
    op.add_column("lessons", sa.Column("independent_practice", sa.Text(), nullable=True))
    op.add_column("lessons", sa.Column("assessment", sa.Text(), nullable=True))
    op.add_column("lessons", sa.Column("review_status", sa.String(), nullable=False, server_default="draft"))
    op.add_column("lessons", sa.Column("reviewed_by", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "fk_lessons_reviewed_by_users",
        "lessons",
        "users",
        ["reviewed_by"],
        ["id"],
    )

    op.create_table(
        "sources",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("lesson_id", sa.UUID(), nullable=False),
        sa.Column("citation", sa.Text(), nullable=False),
        sa.Column("url", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sources_id"), "sources", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_sources_id"), table_name="sources")
    op.drop_table("sources")
    op.drop_constraint("fk_lessons_reviewed_by_users", "lessons", type_="foreignkey")
    op.drop_column("lessons", "reviewed_by")
    op.drop_column("lessons", "review_status")
    op.drop_column("lessons", "assessment")
    op.drop_column("lessons", "independent_practice")
    op.drop_column("lessons", "guided_practice")
    op.drop_column("lessons", "content")
    op.drop_column("lessons", "hook")
    op.drop_column("lessons", "discussion_questions")
    op.drop_column("lessons", "teacher_notes")
    op.drop_column("lessons", "key_concepts")
