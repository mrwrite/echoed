"""add programs assessments and certifications

Revision ID: b7f9c3e12a6d
Revises: e9794a72f032
Create Date: 2026-04-23 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b7f9c3e12a6d"
down_revision: Union[str, None] = "e9794a72f032"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("courses", sa.Column("learning_objectives", sa.Text(), nullable=True))
    op.add_column("courses", sa.Column("skill_tags", sa.JSON(), nullable=True))
    op.add_column("courses", sa.Column("standards_metadata", sa.JSON(), nullable=True))

    op.add_column("lessons", sa.Column("learning_objectives", sa.Text(), nullable=True))
    op.add_column("lessons", sa.Column("skill_tags", sa.JSON(), nullable=True))
    op.add_column("lessons", sa.Column("standards_metadata", sa.JSON(), nullable=True))

    op.create_table(
        "programs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_programs_id"), "programs", ["id"], unique=False)

    op.create_table(
        "program_courses",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("program_id", sa.UUID(), nullable=False),
        sa.Column("course_id", sa.UUID(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"]),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("program_id", "course_id", name="uq_program_course"),
    )
    op.create_index(op.f("ix_program_courses_id"), "program_courses", ["id"], unique=False)

    op.create_table(
        "student_program_progress",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("program_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column("enrolled_on", sa.DateTime(), nullable=False),
        sa.Column("last_activity_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_id", "program_id", name="uq_student_program_progress"),
    )
    op.create_index(op.f("ix_student_program_progress_id"), "student_program_progress", ["id"], unique=False)

    op.create_table(
        "assessments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("lesson_id", sa.UUID(), nullable=True),
        sa.Column("course_id", sa.UUID(), nullable=True),
        sa.Column("program_id", sa.UUID(), nullable=True),
        sa.Column("passing_score", sa.Float(), nullable=False, server_default="70"),
        sa.Column("max_attempts", sa.Integer(), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"]),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_assessments_id"), "assessments", ["id"], unique=False)

    op.create_table(
        "questions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("assessment_id", sa.UUID(), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(), nullable=False, server_default="multiple_choice"),
        sa.Column("choices", sa.JSON(), nullable=True),
        sa.Column("correct_answer", sa.Text(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("points", sa.Float(), nullable=False, server_default="1"),
        sa.Column("order", sa.Integer(), nullable=False, server_default="1"),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_questions_id"), "questions", ["id"], unique=False)

    op.create_table(
        "student_assessment_attempts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("assessment_id", sa.UUID(), nullable=False),
        sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("program_progress_id", sa.UUID(), nullable=True),
        sa.Column("score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("max_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("passed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("submitted_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"]),
        sa.ForeignKeyConstraint(["program_progress_id"], ["student_program_progress.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_student_assessment_attempts_id"), "student_assessment_attempts", ["id"], unique=False)

    op.create_table(
        "student_assessment_answers",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("attempt_id", sa.UUID(), nullable=False),
        sa.Column("question_id", sa.UUID(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("awarded_points", sa.Float(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["attempt_id"], ["student_assessment_attempts.id"]),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_student_assessment_answers_id"), "student_assessment_answers", ["id"], unique=False)

    op.create_table(
        "certifications",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("program_id", sa.UUID(), nullable=False),
        sa.Column("badge_id", sa.UUID(), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["badge_id"], ["badges.id"]),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_certifications_id"), "certifications", ["id"], unique=False)

    op.create_table(
        "certification_requirements",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("certification_id", sa.UUID(), nullable=False),
        sa.Column("requirement_type", sa.String(), nullable=False),
        sa.Column("course_id", sa.UUID(), nullable=True),
        sa.Column("assessment_id", sa.UUID(), nullable=True),
        sa.Column("minimum_score", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"]),
        sa.ForeignKeyConstraint(["certification_id"], ["certifications.id"]),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_certification_requirements_id"), "certification_requirements", ["id"], unique=False)

    op.create_table(
        "student_certifications",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("certification_id", sa.UUID(), nullable=False),
        sa.Column("awarded_at", sa.DateTime(), nullable=False),
        sa.Column("score_snapshot", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["certification_id"], ["certifications.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_id", "certification_id", name="uq_student_certification"),
    )
    op.create_index(op.f("ix_student_certifications_id"), "student_certifications", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_student_certifications_id"), table_name="student_certifications")
    op.drop_table("student_certifications")
    op.drop_index(op.f("ix_certification_requirements_id"), table_name="certification_requirements")
    op.drop_table("certification_requirements")
    op.drop_index(op.f("ix_certifications_id"), table_name="certifications")
    op.drop_table("certifications")
    op.drop_index(op.f("ix_student_assessment_answers_id"), table_name="student_assessment_answers")
    op.drop_table("student_assessment_answers")
    op.drop_index(op.f("ix_student_assessment_attempts_id"), table_name="student_assessment_attempts")
    op.drop_table("student_assessment_attempts")
    op.drop_index(op.f("ix_questions_id"), table_name="questions")
    op.drop_table("questions")
    op.drop_index(op.f("ix_assessments_id"), table_name="assessments")
    op.drop_table("assessments")
    op.drop_index(op.f("ix_student_program_progress_id"), table_name="student_program_progress")
    op.drop_table("student_program_progress")
    op.drop_index(op.f("ix_program_courses_id"), table_name="program_courses")
    op.drop_table("program_courses")
    op.drop_index(op.f("ix_programs_id"), table_name="programs")
    op.drop_table("programs")

    op.drop_column("lessons", "standards_metadata")
    op.drop_column("lessons", "skill_tags")
    op.drop_column("lessons", "learning_objectives")
    op.drop_column("courses", "standards_metadata")
    op.drop_column("courses", "skill_tags")
    op.drop_column("courses", "learning_objectives")
