"""Verify or expire durable audit events without exposing event contents."""

from __future__ import annotations

import argparse
from datetime import datetime
import os
from uuid import UUID

from app.audit import append_audit_event, verify_audit_chain
from app.database import SessionLocal, operational_settings
from app.models import AuditEvent


def _cutoff(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("cutoff must be an ISO-8601 timestamp") from exc


def _organization(value: str | None) -> UUID | None:
    return UUID(value) if value else None


def verify(organization_id: UUID | None) -> int:
    with SessionLocal() as db:
        result = verify_audit_chain(db, organization_id=organization_id)
    print(
        f"audit integrity: {'valid' if result.valid else 'invalid'}; "
        f"scope={result.scope_key}; checked={result.checked}"
    )
    return 0 if result.valid else 2


def retain(args: argparse.Namespace) -> int:
    production = operational_settings.environment == "production"
    if os.getenv("AUDIT_PRESERVATION_HOLD", "false").strip().lower() in {"1", "true", "yes", "on"}:
        raise SystemExit("Audit retention refused: a preservation hold is active.")
    if production and args.apply:
        if not args.ack_production or not args.backup_reference:
            raise SystemExit(
                "Production audit retention requires --ack-production and a verified --backup-reference."
            )
    organization_id = _organization(args.organization_id)
    scope_key = f"organization:{organization_id}" if organization_id else "platform"
    with SessionLocal() as db:
        query = db.query(AuditEvent).filter(
            AuditEvent.scope_key == scope_key,
            AuditEvent.created_at < args.before,
        )
        count = query.count()
        if not args.apply:
            print(f"audit retention dry-run: scope={scope_key}; eligible={count}")
            return 0
        query.delete(synchronize_session=False)
        append_audit_event(
            db,
            action="audit.retention.performed",
            actor_id=None,
            actor_role="operator",
            target_type="audit_event_set",
            target_id=scope_key,
            organization_id=organization_id,
            after={"deleted_count": count, "cutoff": args.before.isoformat()},
            reason_code="retention_policy",
        )
        db.commit()
    print(f"audit retention applied: scope={scope_key}; deleted={count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    verify_parser = subcommands.add_parser("verify")
    verify_parser.add_argument("--organization-id")
    retention_parser = subcommands.add_parser("retain")
    retention_parser.add_argument("--before", required=True, type=_cutoff)
    retention_parser.add_argument("--organization-id")
    retention_parser.add_argument("--apply", action="store_true")
    retention_parser.add_argument("--ack-production", action="store_true")
    retention_parser.add_argument("--backup-reference")
    args = parser.parse_args()
    if args.command == "verify":
        return verify(_organization(args.organization_id))
    return retain(args)


if __name__ == "__main__":
    raise SystemExit(main())
