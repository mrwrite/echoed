## 1. Baseline and contracts

- [x] 1.1 Record the starting branch, commit, dirty-tree/archive states, actual test baselines, existing security-event coverage, database/migration architecture, and audit privacy boundary
- [x] 1.2 Publish the action catalog, access/scope matrix, minimized field policy, retention ownership, integrity threat boundary, and operational audit-vs-log distinction
- [x] 1.3 Strictly validate the complete proposal, design, new capability spec, operational-readiness delta, and task plan

## 2. Persistence and integrity foundation

- [x] 2.1 Add the explicit append-only audit-event SQLAlchemy model, indexes, schema version, and Alembic migration with PostgreSQL and SQLite compatibility
- [x] 2.2 Implement centralized action definitions, payload allowlists/redaction rejection, canonical serialization, per-scope hash chaining, and integrity verification
- [x] 2.3 Implement transaction-bound append semantics that flush without independently committing and emit bounded operational metrics/logs
- [x] 2.4 Add guarded dry-run-first retention and integrity-verification operator tooling with production acknowledgement, backup reference, and preservation-hold controls

## 3. High-impact mutation coverage

- [x] 3.1 Capture successful platform-role changes and account deletion with minimized before/after state in the mutation transaction
- [x] 3.2 Capture supported organization invitation and membership mutations with organization scope in the mutation transaction
- [x] 3.3 Capture supported forum moderation mutations with author/moderator scope in the mutation transaction
- [x] 3.4 Capture supported Course Studio publish, review, and restore transitions with content identifiers but no course graph/content
- [x] 3.5 Verify denied, failed, and rolled-back mutations do not produce misleading successful durable events

## 4. Scoped review and export APIs

- [x] 4.1 Add explicit minimized audit summary/detail/filter/export schemas without ORM serialization
- [x] 4.2 Add platform-admin and active-organization-admin authorization dependencies with cross-organization concealment
- [x] 4.3 Add bounded cursor-paginated list/detail endpoints with allowlisted validation and stable ordering
- [x] 4.4 Add capped formula-safe CSV export using identical scope/filter rules and durable export-event capture
- [x] 4.5 Add capture/read/export/integrity/retention metrics and redacted structured diagnostics without high-cardinality labels

## 5. Administrative review experience

- [x] 5.1 Add frontend audit-event models/service with minimized response compatibility and request-reference error handling
- [x] 5.2 Add a role-guarded Platform Admin audit route, navigation entry, accessible filters, loading/empty/error/list/detail/pagination states, and bounded export action
- [x] 5.3 Add Angular tests for authorization-aligned visibility, minimized rendering, filter/pagination/export behavior, accessible failures, and stale-data clearing

## 6. Verification and operations

- [x] 6.1 Add backend tests for schema privacy, atomicity, rollback, action coverage, chain integrity/tampering/concurrency, append-only behavior, scoped reads, cross-organization denial, pagination, export safety, retention, and configuration
- [x] 6.2 Update backup/restore tooling and drills to preserve audit rows/integrity metadata and verify the restored chain
- [x] 6.3 Add stable Playwright coverage for authorized review and denied direct-route access where practical without exposing internal event contents
- [x] 6.4 Publish audit architecture, privacy/access, retention/export, integrity, incident/backup, operator runbook, baseline, and exact verification evidence; update canonical security/operations/roadmap documents
- [ ] 6.5 Run complete backend, Angular, Playwright, production build, dependency audit, configured lint/format/static checks, strict OpenSpec validation, secret/artifact checks, and `git diff --check` without baseline regression
