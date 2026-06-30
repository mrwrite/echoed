"""add access grants

Revision ID: b3d2c1e4f607
Revises: a2f4c6d8e9b1
Create Date: 2026-06-30 16:55:00.000000
"""

from datetime import datetime
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


revision: str = "b3d2c1e4f607"
down_revision: Union[str, Sequence[str], None] = "a2f4c6d8e9b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "access_grants",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column("workspace_id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=True),
        sa.Column("grant_type", sa.String(), nullable=False, server_default="manual"),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column("source", sa.String(), nullable=False, server_default="manual"),
        sa.Column("starts_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "product_id", "grant_type", name="uq_access_grant_user_product_type"),
    )
    op.create_index(op.f("ix_access_grants_id"), "access_grants", ["id"], unique=False)
    op.create_index("ix_access_grants_user_id", "access_grants", ["user_id"], unique=False)
    op.create_index("ix_access_grants_product_id", "access_grants", ["product_id"], unique=False)
    op.create_index("ix_access_grants_workspace_id", "access_grants", ["workspace_id"], unique=False)
    _backfill_enrollment_grants()


def downgrade() -> None:
    op.drop_index("ix_access_grants_workspace_id", table_name="access_grants")
    op.drop_index("ix_access_grants_product_id", table_name="access_grants")
    op.drop_index("ix_access_grants_user_id", table_name="access_grants")
    op.drop_index(op.f("ix_access_grants_id"), table_name="access_grants")
    op.drop_table("access_grants")


def _backfill_enrollment_grants() -> None:
    connection = op.get_bind()
    now = datetime.utcnow()
    rows = []
    seen: set[tuple[object, object]] = set()

    course_rows = connection.execute(
        sa.text(
            """
            SELECT
                sc.student_id AS user_id,
                sc.status AS enrollment_status,
                sc.enrolled_on AS starts_at,
                p.id AS product_id,
                p.workspace_id AS workspace_id,
                p.project_id AS project_id
            FROM student_courses sc
            JOIN products p ON p.course_id = sc.course_id
            """
        )
    ).mappings()
    for row in course_rows:
        key = (row["user_id"], row["product_id"])
        if key in seen:
            continue
        seen.add(key)
        rows.append(_grant_row(row, now, "student_course_backfill"))

    program_rows = connection.execute(
        sa.text(
            """
            SELECT
                spp.student_id AS user_id,
                spp.status AS enrollment_status,
                spp.enrolled_on AS starts_at,
                p.id AS product_id,
                p.workspace_id AS workspace_id,
                p.project_id AS project_id
            FROM student_program_progress spp
            JOIN products p ON p.program_id = spp.program_id
            """
        )
    ).mappings()
    for row in program_rows:
        key = (row["user_id"], row["product_id"])
        if key in seen:
            continue
        seen.add(key)
        rows.append(_grant_row(row, now, "student_program_progress_backfill"))

    if rows:
        op.bulk_insert(
            sa.table(
                "access_grants",
                sa.column("id", sa.UUID()),
                sa.column("user_id", sa.UUID()),
                sa.column("product_id", sa.UUID()),
                sa.column("workspace_id", sa.UUID()),
                sa.column("project_id", sa.UUID()),
                sa.column("grant_type", sa.String()),
                sa.column("status", sa.String()),
                sa.column("source", sa.String()),
                sa.column("starts_at", sa.DateTime()),
                sa.column("expires_at", sa.DateTime()),
                sa.column("revoked_at", sa.DateTime()),
                sa.column("metadata", sa.JSON()),
                sa.column("created_at", sa.DateTime()),
                sa.column("updated_at", sa.DateTime()),
            ),
            rows,
        )


def _grant_row(row, now: datetime, source: str) -> dict:
    enrollment_status = (row["enrollment_status"] or "active").lower()
    status = "revoked" if enrollment_status == "withdrawn" else "active"
    revoked_at = now if status == "revoked" else None
    return {
        "id": uuid.uuid4(),
        "user_id": row["user_id"],
        "product_id": row["product_id"],
        "workspace_id": row["workspace_id"],
        "project_id": row["project_id"],
        "grant_type": "enrollment",
        "status": status,
        "source": source,
        "starts_at": row["starts_at"],
        "expires_at": None,
        "revoked_at": revoked_at,
        "metadata": {"source_enrollment_status": enrollment_status},
        "created_at": now,
        "updated_at": now,
    }
