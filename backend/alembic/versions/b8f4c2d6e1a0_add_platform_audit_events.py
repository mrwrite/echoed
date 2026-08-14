"""Add durable platform audit events.

Revision ID: b8f4c2d6e1a0
Revises: 9a7b6c5d4e3f
Create Date: 2026-08-13 18:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "b8f4c2d6e1a0"
down_revision = "9a7b6c5d4e3f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("schema_version", sa.Integer(), nullable=False),
        sa.Column("scope_key", sa.String(length=80), nullable=False),
        sa.Column("scope_sequence", sa.Integer(), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_role", sa.String(length=40), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=False),
        sa.Column("outcome", sa.String(length=24), nullable=False),
        sa.Column("target_type", sa.String(length=60), nullable=False),
        sa.Column("target_id", sa.String(length=100), nullable=False),
        sa.Column("request_id", sa.String(length=128), nullable=True),
        sa.Column("correlation_id", sa.String(length=64), nullable=True),
        sa.Column("reason_code", sa.String(length=80), nullable=True),
        sa.Column("before_state", sa.JSON(), nullable=False),
        sa.Column("after_state", sa.JSON(), nullable=False),
        sa.Column("previous_hash", sa.String(length=64), nullable=False),
        sa.Column("event_hash", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scope_key", "scope_sequence", name="uq_audit_events_scope_sequence"),
        sa.UniqueConstraint("event_hash"),
    )
    op.create_index("ix_audit_events_scope_created", "audit_events", ["scope_key", "created_at", "id"])
    op.create_index("ix_audit_events_action_created", "audit_events", ["action", "created_at"])
    op.create_index("ix_audit_events_actor_created", "audit_events", ["actor_id", "created_at"])
    op.create_index(
        "ix_audit_events_target_created", "audit_events", ["target_type", "target_id", "created_at"]
    )


def downgrade() -> None:
    op.drop_index("ix_audit_events_target_created", table_name="audit_events")
    op.drop_index("ix_audit_events_actor_created", table_name="audit_events")
    op.drop_index("ix_audit_events_action_created", table_name="audit_events")
    op.drop_index("ix_audit_events_scope_created", table_name="audit_events")
    op.drop_table("audit_events")
