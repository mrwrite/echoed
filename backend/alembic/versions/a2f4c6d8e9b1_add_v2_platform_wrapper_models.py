"""add v2 platform wrapper models

Revision ID: a2f4c6d8e9b1
Revises: 71d5d3a8f680, 9f1c2d3e4a5b
Create Date: 2026-06-30 12:35:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import uuid
from datetime import datetime


revision: str = "a2f4c6d8e9b1"
down_revision: Union[str, tuple[str, str], None] = ("71d5d3a8f680", "9f1c2d3e4a5b")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "workspaces",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", name="uq_workspace_organization"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_workspaces_id"), "workspaces", ["id"], unique=False)
    op.create_index(op.f("ix_workspaces_slug"), "workspaces", ["slug"], unique=False)

    op.create_table(
        "projects",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("workspace_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_projects_id"), "projects", ["id"], unique=False)
    op.create_index("ix_projects_workspace_id", "projects", ["workspace_id"], unique=False)

    op.create_table(
        "products",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("workspace_id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=True),
        sa.Column("course_id", sa.UUID(), nullable=True),
        sa.Column("program_id", sa.UUID(), nullable=True),
        sa.Column("product_type", sa.String(), nullable=False, server_default="course"),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="draft"),
        sa.Column("review_state", sa.String(), nullable=False, server_default="not_reviewed"),
        sa.Column("access_state", sa.String(), nullable=False, server_default="private"),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"]),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("course_id", name="uq_product_course"),
        sa.UniqueConstraint("program_id", name="uq_product_program"),
    )
    op.create_index(op.f("ix_products_id"), "products", ["id"], unique=False)
    op.create_index("ix_products_workspace_id", "products", ["workspace_id"], unique=False)
    op.create_index("ix_products_project_id", "products", ["project_id"], unique=False)

    op.create_table(
        "knowledge_sources",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("workspace_id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("source_id", sa.UUID(), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("source_type", sa.String(), nullable=False, server_default="document"),
        sa.Column("uri", sa.String(), nullable=True),
        sa.Column("citation", sa.Text(), nullable=True),
        sa.Column("content_hash", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="available"),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_knowledge_sources_id"), "knowledge_sources", ["id"], unique=False)
    op.create_index("ix_knowledge_sources_project_id", "knowledge_sources", ["project_id"], unique=False)

    op.create_table(
        "generation_runs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("workspace_id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="queued"),
        sa.Column("provider", sa.String(), nullable=True),
        sa.Column("model_name", sa.String(), nullable=True),
        sa.Column("prompt", sa.Text(), nullable=True),
        sa.Column("output_summary", sa.Text(), nullable=True),
        sa.Column("input_metadata", sa.JSON(), nullable=True),
        sa.Column("output_metadata", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_generation_runs_id"), "generation_runs", ["id"], unique=False)
    op.create_index("ix_generation_runs_project_id", "generation_runs", ["project_id"], unique=False)

    op.create_table(
        "artifacts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("workspace_id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=True),
        sa.Column("generation_run_id", sa.UUID(), nullable=True),
        sa.Column("knowledge_source_id", sa.UUID(), nullable=True),
        sa.Column("artifact_type", sa.String(), nullable=False, server_default="documentation"),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("uri", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="draft"),
        sa.Column("review_state", sa.String(), nullable=False, server_default="review_required"),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["generation_run_id"], ["generation_runs.id"]),
        sa.ForeignKeyConstraint(["knowledge_source_id"], ["knowledge_sources.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_artifacts_id"), "artifacts", ["id"], unique=False)
    op.create_index("ix_artifacts_project_id", "artifacts", ["project_id"], unique=False)

    _backfill_workspace_and_products()


def downgrade() -> None:
    op.drop_index("ix_artifacts_project_id", table_name="artifacts")
    op.drop_index(op.f("ix_artifacts_id"), table_name="artifacts")
    op.drop_table("artifacts")

    op.drop_index("ix_generation_runs_project_id", table_name="generation_runs")
    op.drop_index(op.f("ix_generation_runs_id"), table_name="generation_runs")
    op.drop_table("generation_runs")

    op.drop_index("ix_knowledge_sources_project_id", table_name="knowledge_sources")
    op.drop_index(op.f("ix_knowledge_sources_id"), table_name="knowledge_sources")
    op.drop_table("knowledge_sources")

    op.drop_index("ix_products_project_id", table_name="products")
    op.drop_index("ix_products_workspace_id", table_name="products")
    op.drop_index(op.f("ix_products_id"), table_name="products")
    op.drop_table("products")

    op.drop_index("ix_projects_workspace_id", table_name="projects")
    op.drop_index(op.f("ix_projects_id"), table_name="projects")
    op.drop_table("projects")

    op.drop_index(op.f("ix_workspaces_slug"), table_name="workspaces")
    op.drop_index(op.f("ix_workspaces_id"), table_name="workspaces")
    op.drop_table("workspaces")


def _backfill_workspace_and_products() -> None:
    connection = op.get_bind()
    now = datetime.utcnow()
    workspace_ids_by_org: dict[str, uuid.UUID] = {}

    organizations = connection.execute(sa.text("SELECT id, name FROM organizations")).fetchall()
    for organization_id, organization_name in organizations:
        workspace_id = uuid.uuid4()
        workspace_ids_by_org[str(organization_id)] = workspace_id
        connection.execute(
            sa.text(
                "INSERT INTO workspaces (id, organization_id, name, status, created_at, updated_at) "
                "VALUES (:id, :organization_id, :name, 'active', :created_at, :updated_at)"
            ),
            {
                "id": workspace_id,
                "organization_id": organization_id,
                "name": organization_name,
                "created_at": now,
                "updated_at": now,
            },
        )

    legacy_workspace_id: uuid.UUID | None = None

    def legacy_workspace() -> uuid.UUID:
        nonlocal legacy_workspace_id
        if legacy_workspace_id is None:
            legacy_workspace_id = uuid.uuid4()
            connection.execute(
                sa.text(
                    "INSERT INTO workspaces (id, name, status, created_at, updated_at) "
                    "VALUES (:id, 'Legacy EchoEd Workspace', 'active', :created_at, :updated_at)"
                ),
                {"id": legacy_workspace_id, "created_at": now, "updated_at": now},
            )
        return legacy_workspace_id

    courses = connection.execute(
        sa.text("SELECT id, title, description, organization_id FROM courses")
    ).fetchall()
    for course_id, title, description, organization_id in courses:
        workspace_id = (
            workspace_ids_by_org.get(str(organization_id))
            if organization_id is not None
            else legacy_workspace()
        )
        if workspace_id is None:
            workspace_id = legacy_workspace()
        connection.execute(
            sa.text(
                "INSERT INTO products "
                "(id, workspace_id, course_id, product_type, title, description, status, review_state, access_state, created_at, updated_at) "
                "VALUES (:id, :workspace_id, :course_id, 'course', :title, :description, 'active', "
                "'runtime_authoritative', 'existing_runtime', :created_at, :updated_at)"
            ),
            {
                "id": uuid.uuid4(),
                "workspace_id": workspace_id,
                "course_id": course_id,
                "title": title,
                "description": description,
                "created_at": now,
                "updated_at": now,
            },
        )

    programs = connection.execute(
        sa.text("SELECT id, title, description, organization_id FROM programs")
    ).fetchall()
    for program_id, title, description, organization_id in programs:
        workspace_id = (
            workspace_ids_by_org.get(str(organization_id))
            if organization_id is not None
            else legacy_workspace()
        )
        if workspace_id is None:
            workspace_id = legacy_workspace()
        connection.execute(
            sa.text(
                "INSERT INTO products "
                "(id, workspace_id, program_id, product_type, title, description, status, review_state, access_state, created_at, updated_at) "
                "VALUES (:id, :workspace_id, :program_id, 'learning_path', :title, :description, 'active', "
                "'runtime_authoritative', 'existing_runtime', :created_at, :updated_at)"
            ),
            {
                "id": uuid.uuid4(),
                "workspace_id": workspace_id,
                "program_id": program_id,
                "title": title,
                "description": description,
                "created_at": now,
                "updated_at": now,
            },
        )
