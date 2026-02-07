"""add orgs and course versions

Revision ID: 2024_10_01_orgs
Revises: ec240e08c8e0
Create Date: 2024-10-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid
from datetime import datetime

# revision identifiers, used by Alembic.
revision = "2024_10_01_orgs"
down_revision = "ec240e08c8e0"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("type", sa.Enum(
            "school",
            "homeschool",
            "district",
            "instructor",
            "personal",
            name="organization_type_enum",
        ), nullable=False),
        sa.Column("country", sa.String(), nullable=True),
        sa.Column("timezone", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "organization_memberships",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role", sa.Enum(
            "org_admin",
            "content_admin",
            "teacher",
            "parent",
            "student",
            "instructor",
            "viewer",
            name="organization_role_enum",
        ), nullable=False),
        sa.Column("status", sa.Enum(
            "active",
            "invited",
            "inactive",
            name="membership_status_enum",
        ), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "organization_invites",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("role", sa.Enum(
            "org_admin",
            "content_admin",
            "teacher",
            "parent",
            "student",
            "instructor",
            "viewer",
            name="invite_role_enum",
        ), nullable=False),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("accepted_at", sa.DateTime(), nullable=True),
        sa.Column("invited_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_organization_invites_token", "organization_invites", ["token"], unique=True)

    op.create_table(
        "user_preferences",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("locale", sa.String(), nullable=False, server_default="en"),
        sa.Column("timezone", sa.String(), nullable=True),
        sa.Column("theme", sa.String(), nullable=False, server_default="system"),
        sa.Column("large_text", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("dyslexia_font", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("preferred_mode", sa.String(), nullable=False, server_default="student"),
        sa.Column("reading_level_mode", sa.String(), nullable=False, server_default="standard"),
    )

    op.add_column("courses", sa.Column("subject", sa.String(), nullable=True))
    op.add_column("courses", sa.Column("age_band_min", sa.Integer(), nullable=True))
    op.add_column("courses", sa.Column("age_band_max", sa.Integer(), nullable=True))
    op.add_column("courses", sa.Column("default_locale", sa.String(), nullable=False, server_default="en"))
    op.add_column("courses", sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True))
    op.add_column("courses", sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=True))

    op.create_table(
        "course_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id"), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.Enum("draft", "published", "archived", name="course_version_status_enum"), nullable=False, server_default="draft"),
        sa.Column("changelog", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("published_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )

    op.add_column("units", sa.Column("course_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("course_versions.id"), nullable=True))

    op.create_table(
        "sections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("course_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("course_versions.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("mode", sa.Enum("in_person", "remote", "hybrid", "home", name="section_mode_enum"), nullable=False, server_default="remote"),
        sa.Column("start_date", sa.DateTime(), nullable=True),
        sa.Column("end_date", sa.DateTime(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "enrollments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("section_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sections.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role_in_section", sa.String(), nullable=False, server_default="student"),
        sa.Column("status", sa.Enum("active", "pending", "completed", "withdrawn", name="enrollment_status_enum"), nullable=False, server_default="active"),
        sa.Column("enrolled_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "lesson_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("section_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sections.id"), nullable=False),
        sa.Column("lesson_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lessons.id"), nullable=False),
        sa.Column("started_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("section_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sections.id"), nullable=False),
        sa.Column("target_type", sa.Enum("unit", "lesson", name="assignment_target_enum"), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("due_at", sa.DateTime(), nullable=True),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "assignment_submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("assignment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assignments.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.Enum("not_started", "submitted", "completed", name="assignment_submission_status_enum"), nullable=False, server_default="not_started"),
        sa.Column("submitted_at", sa.DateTime(), nullable=True),
    )

    op.add_column("student_courses", sa.Column("section_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sections.id"), nullable=True))
    op.add_column("student_unit_progress", sa.Column("section_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sections.id"), nullable=True))
    op.add_column("segment_progress", sa.Column("section_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sections.id"), nullable=True))

    # Data migration: create personal org per user and course versions.
    connection = op.get_bind()
    users = connection.execute(sa.text("SELECT id, firstname FROM users")).fetchall()
    for user_id, firstname in users:
        org_id = uuid.uuid4()
        connection.execute(
            sa.text(
                "INSERT INTO organizations (id, name, type, created_at) VALUES (:id, :name, :type, :created_at)"
            ),
            {
                "id": org_id,
                "name": f"{firstname}'s Personal Org",
                "type": "personal",
                "created_at": datetime.utcnow(),
            },
        )
        connection.execute(
            sa.text(
                "INSERT INTO organization_memberships (id, organization_id, user_id, role, status, created_at)"
                " VALUES (:id, :organization_id, :user_id, :role, :status, :created_at)"
            ),
            {
                "id": uuid.uuid4(),
                "organization_id": org_id,
                "user_id": user_id,
                "role": "org_admin",
                "status": "active",
                "created_at": datetime.utcnow(),
            },
        )
        connection.execute(
            sa.text(
                "INSERT INTO user_preferences (user_id, locale, theme, large_text, dyslexia_font, preferred_mode, reading_level_mode)"
                " VALUES (:user_id, 'en', 'system', false, false, 'student', 'standard')"
            ),
            {"user_id": user_id},
        )

    courses = connection.execute(sa.text("SELECT id FROM courses")).fetchall()
    for (course_id,) in courses:
        version_id = uuid.uuid4()
        connection.execute(
            sa.text(
                "INSERT INTO course_versions (id, course_id, version_number, status, created_at)"
                " VALUES (:id, :course_id, 1, 'published', :created_at)"
            ),
            {"id": version_id, "course_id": course_id, "created_at": datetime.utcnow()},
        )
        connection.execute(
            sa.text("UPDATE units SET course_version_id = :version_id WHERE course_id = :course_id"),
            {"version_id": version_id, "course_id": course_id},
        )


def downgrade():
    op.drop_column("segment_progress", "section_id")
    op.drop_column("student_unit_progress", "section_id")
    op.drop_column("student_courses", "section_id")

    op.drop_table("assignment_submissions")
    op.drop_table("assignments")
    op.drop_table("lesson_sessions")
    op.drop_table("enrollments")
    op.drop_table("sections")

    op.drop_column("units", "course_version_id")
    op.drop_table("course_versions")

    op.drop_column("courses", "organization_id")
    op.drop_column("courses", "created_by")
    op.drop_column("courses", "default_locale")
    op.drop_column("courses", "age_band_max")
    op.drop_column("courses", "age_band_min")
    op.drop_column("courses", "subject")

    op.drop_table("user_preferences")
    op.drop_index("ix_organization_invites_token", table_name="organization_invites")
    op.drop_table("organization_invites")
    op.drop_table("organization_memberships")
    op.drop_table("organizations")

    op.execute("DROP TYPE IF EXISTS assignment_submission_status_enum")
    op.execute("DROP TYPE IF EXISTS assignment_target_enum")
    op.execute("DROP TYPE IF EXISTS enrollment_status_enum")
    op.execute("DROP TYPE IF EXISTS section_mode_enum")
    op.execute("DROP TYPE IF EXISTS course_version_status_enum")
    op.execute("DROP TYPE IF EXISTS membership_status_enum")
    op.execute("DROP TYPE IF EXISTS invite_role_enum")
    op.execute("DROP TYPE IF EXISTS organization_role_enum")
    op.execute("DROP TYPE IF EXISTS organization_type_enum")
