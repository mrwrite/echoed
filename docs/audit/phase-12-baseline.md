# Phase 12 Platform Audit Events Baseline

Recorded 2026-08-13 before audit implementation.

- Branch/commit: `aqw-echoed-dev` / `e67300b3c5a0d2f720eca8fa1c968eb02a610308`.
- Working tree: clean before Phase 11 archival; Phase 11 archive/spec-sync changes became the intentional initial dirty state for this phase.
- OpenSpec: `establish-operational-readiness` was complete and strictly valid, then synced and archived at `openspec/changes/archive/2026-08-13-establish-operational-readiness`. Phase 8 and Phase 10 remain completed active changes.
- Verified prior baselines: 299 backend, 308 Angular, and 23 Playwright tests; production Angular build and production npm audit passed.
- Existing event architecture: `security_event()` emits recursively redacted structured diagnostic logs and low-cardinality metrics. Events are ephemeral, non-transactional, and not an audit ledger.
- Existing event coverage: authentication failure, rate limiting, role changes, user deletion, final-admin denial, invitation creation, upload rejection, moderator deletion, authorization denial, and Course Studio operational outcomes.
- Database/migrations: SQLAlchemy ORM, Alembic single head `9a7b6c5d4e3f`, PostgreSQL production intent, SQLite test fixtures. Normal production startup does not migrate automatically.
- Privacy boundary: no passwords, hashes, bearer/invitation/reset tokens, cookies, authorization headers, private learner/course content, assessment answers, uploaded bytes, filenames, emails, or names belong in durable events.
- Persistent-state baseline: database and upload paths are operator-owned; repository backup drills accept acknowledged non-production SQLite/filesystem data only.

This baseline does not claim external tamper resistance, WORM storage, legal retention compliance, or production audit readiness.
