"""Normalize progress status enum values

Revision ID: f2b7c9d1e4a6
Revises: d4e5f6a7b8c9
Create Date: 2026-07-02 08:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision = "f2b7c9d1e4a6"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None


def _rename_progress_status_values(pairs: list[tuple[str, str]]) -> None:
    conn = op.get_bind()
    for old_value, new_value in pairs:
        conn.execute(
            sa.text(
                """
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1
                        FROM pg_enum e
                        JOIN pg_type t ON t.oid = e.enumtypid
                        WHERE t.typname = 'progress_status_enum'
                          AND e.enumlabel = :old_value
                    )
                    AND NOT EXISTS (
                        SELECT 1
                        FROM pg_enum e
                        JOIN pg_type t ON t.oid = e.enumtypid
                        WHERE t.typname = 'progress_status_enum'
                          AND e.enumlabel = :new_value
                    ) THEN
                        EXECUTE format(
                            'ALTER TYPE progress_status_enum RENAME VALUE %L TO %L',
                            :old_value,
                            :new_value
                        );
                    END IF;
                END $$;
                """
            ),
            {"old_value": old_value, "new_value": new_value},
        )


def upgrade() -> None:
    _rename_progress_status_values(
        [
            ("NOT_STARTED", "not_started"),
            ("IN_PROGRESS", "in_progress"),
            ("SKIPPED", "skipped"),
            ("DELIVERED", "delivered"),
            ("COMPLETED", "completed"),
        ]
    )


def downgrade() -> None:
    _rename_progress_status_values(
        [
            ("not_started", "NOT_STARTED"),
            ("in_progress", "IN_PROGRESS"),
            ("skipped", "SKIPPED"),
            ("delivered", "DELIVERED"),
            ("completed", "COMPLETED"),
        ]
    )
