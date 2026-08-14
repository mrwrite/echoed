## Why

EchoEd's structured security logs are intentionally ephemeral and cannot provide administrators or incident responders with durable, attributable evidence of high-impact actions. With security, observability, and operational-readiness foundations complete, the platform now needs a privacy-minimized audit record whose persistence and access rules are enforced independently from diagnostic logging.

## What Changes

- Add an append-only audit-event persistence model with actor, action, target, organization, outcome, request/correlation context, minimized before/after state, timestamps, and integrity-chain metadata.
- Record approved high-impact platform and organization mutations in the same database transaction as the affected state, so a successful mutation cannot silently omit its audit event.
- Add explicit platform-global and organization-scoped audit read APIs with bounded filtering, cursor pagination, concealment, retention metadata, and safe export.
- Prevent application-level update/delete operations on audit records and provide integrity verification and retention tooling that preserves deletion evidence without presenting the store as cryptographically tamper-proof infrastructure.
- Add an accessible administrative review surface using minimized schemas and existing role/navigation patterns.
- Add privacy, retention, access-control, incident, backup, and operational documentation plus regression evidence.
- Preserve structured operational/security logs as a separate diagnostic signal; they are not replaced by the durable audit store.

## Capabilities

### New Capabilities

- `platform-audit-events`: Durable append-only administrative event capture, transactional guarantees, scoped review/export, integrity verification, retention, privacy, and operational ownership.

### Modified Capabilities

- `platform-operational-readiness`: Extend the persistent-state, backup/restore, and operational-drill contract to include the audit-event store and integrity verification.

## Impact

- Backend: SQLAlchemy model, Alembic migration, audit service, authorization dependencies, APIs/schemas, high-impact mutation instrumentation, integrity/retention operator commands, metrics/log integration, and tests.
- Frontend: API models/service, guarded Platform Admin audit review route, accessible filtering/detail/export behavior, and tests.
- Operations/security: backup classification, retention policy, incident preservation, privacy rules, and verification evidence.
- No commercial dependency, external ledger, authentication redesign, distributed state, hosting change, or general application feature work is introduced.
