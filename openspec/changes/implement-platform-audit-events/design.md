## Context

Phase 8 emits privacy-safe security events and Phase 10 routes them through structured, redacted logs with request/correlation IDs. Those records are operational diagnostics: they are process-local or deployment-log dependent, have no transactional relationship to database mutations, and provide no retention, scoped review, or integrity contract. Phase 11 established backup/restore and operational ownership but explicitly deferred durable audit events.

EchoEd is a FastAPI/SQLAlchemy application with Alembic migrations, PostgreSQL production intent, SQLite test support, explicit platform and organization authorization helpers, an Angular administrative shell, and no background worker. The solution must work in that architecture without introducing a queue, commercial system, or external ledger.

## Goals / Non-Goals

**Goals:**

- Persist a minimized, attributable event for approved high-impact mutations in the same transaction as the mutation.
- Make persisted events append-only through the application service and database permissions/guardrails available to the repository.
- Provide explicit platform and organization read authorization, stable filtering, bounded pagination, and safe CSV export.
- Preserve request/correlation context while excluding credentials, content bodies, learner answers, filenames, and unnecessary personal data.
- Detect missing/reordered/modified records through a per-scope hash chain and expose verification to operators.
- Define retention, legal/incident hold boundaries, backup/restore ownership, and safe operational verification.

**Non-Goals:**

- A cryptographically external or independently witnessed ledger.
- A commercial SIEM, centralized log service, blockchain, event bus, queue, or new hosting system.
- Authentication/authorization redesign, distributed rate limiting, or product analytics.
- Capturing ordinary reads, every CRUD operation, raw request bodies, course content, assessment answers, or user-provided files.
- Replacing operational/security logging; successful audit persistence may emit a diagnostic event, but the stores retain distinct purposes.

## Decisions

### Persist immutable, minimized rows

`audit_events` stores a UUID, UTC creation time, stable action/category/outcome, actor ID/role snapshot, target type/ID, optional organization ID, request/correlation IDs, JSON before/after summaries, reason code, schema version, previous hash, and event hash. There is no update endpoint or ORM mutation service. Values are allowlisted and recursively privacy-validated before persistence.

Alternative considered: persist the existing log payload verbatim. Rejected because log fields are not a durable schema and can include diagnostic details inappropriate for administrative review.

### Transactional capture through one service

High-impact routes call `append_audit_event(db, ...)` before the route's existing commit. The service adds and flushes the row but never commits independently. A flush failure aborts the business mutation. Failed/denied attempts remain operational security logs unless a deliberate durable failure event can be written without creating misleading transactional evidence.

Alternative considered: capture from middleware after responses. Rejected because it cannot guarantee atomicity, reconstruct safe before/after state, or distinguish rolled-back work.

### Start with approved high-impact actions

Initial coverage includes platform-role changes, account deletion, organization invitation creation/acceptance and membership changes supported by current routes, forum moderation deletion, and Course Studio publish/review/restore transitions that currently exist. Coverage is maintained as an explicit catalog and regression-tested. Unsupported product actions are not invented.

### Per-scope chained integrity evidence

Each event hashes canonical versioned content plus the previous hash and sequence for its scope (`platform` or organization UUID). A PostgreSQL transaction advisory lock serializes even concurrent first writes, and a unique scope/sequence constraint prevents forks. An operator verifier recomputes retained chains and fails on modification or reordering. Intentional retention can remove a prefix, so deletion before the retained boundary cannot be proven without an external anchor. This is tamper-evident application data, not tamper-proof evidence against a database superuser; external anchoring remains deferred infrastructure.

### Scoped, minimized reads

`admin` and `super_admin` can read the platform feed. Active organization administrators can read only events whose organization matches their membership and cannot select another scope by ID. Responses expose display-safe IDs and state summaries, never joined user/profile/course bodies. Missing and concealed cross-organization resources use the existing security error policy. Exports apply the same query policy, filters, limits, and schema.

### Bounded retention with explicit preservation

Repository code exposes a dry-run-first operator retention command. Production deletion requires an explicit cutoff, environment acknowledgement, prior backup, and no active preservation hold. Retention deletion is performed only by operator tooling, emits a retained tombstone/summary event in the surviving chain, and is never available through the public API. Default policy documentation retains security administration events for 365 days, subject to operator/legal policy.

### Angular review surface remains operationally narrow

The existing Admin area gains an audit-events list/detail surface for allowed platform administrators. Organization-scoped review remains API-ready and can be linked from Organization navigation only where the existing shell can prove the active role. Filters are action/category/outcome/time; raw IDs are optional support fields. CSV export is a deliberate user action with accessible success/failure status.

## Risks / Trade-offs

- **Database administrators can still alter both rows and hashes** → Document the threat boundary; restrict database credentials, back up separately, verify chains, and defer external anchoring/WORM storage.
- **Concurrent events could fork a scope chain** → Lock the latest scope row in PostgreSQL and test sequential integrity; SQLite remains a single-process test limitation.
- **Instrumentation gaps can create false confidence** → Maintain a canonical action catalog and tests that successful sensitive mutations create exactly one event while rollback creates none.
- **Before/after state can leak data** → Permit only primitive allowlisted keys per action and reject sensitive key names/nested payloads centrally.
- **Audit storage grows indefinitely** → Index query dimensions, paginate reads, document capacity monitoring, and provide guarded retention tooling.
- **Account deletion removes actor/target joins** → Store UUID and role snapshots without foreign-key cascade dependencies; do not denormalize names or emails.
- **Exports increase disclosure risk** → Require the same authorization as reads, cap rows, omit private fields, use attachment-safe CSV encoding, and durably record export actions.

## Migration Plan

1. Deploy the additive `audit_events` table and indexes before application code that writes events.
2. Deploy backend capture/read/export/integrity behavior; verify readiness and a disposable mutation/event transaction.
3. Deploy the Angular review surface after the read API is available.
4. Add the audit table to production backup classification and execute isolated backup/restore plus chain verification.
5. Rollback application code only while leaving the additive table in place. Do not drop accumulated audit history during routine rollback.

## Open Questions

- Production retention may need jurisdiction-specific adjustment; the repository defines a safe default and operator mechanism, not legal advice.
- External anchoring, WORM storage, and independent audit replication depend on future infrastructure selection.
- Organization audit UI expansion depends on whether organization administrators require self-service review in the first operational rollout; backend scope remains mandatory either way.
