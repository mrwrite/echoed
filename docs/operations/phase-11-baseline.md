# Phase 11 Operational Readiness Baseline

Recorded 2026-08-07 before implementation.

| Item | Starting evidence |
| --- | --- |
| Branch / commit | `aqw-echoed-dev` / `c6336fa79458c08da75746954615a86522e766a8` |
| Working tree | Dirty with extensive user-authored Phase 8, Course Studio, and Phase 10 work. It was preserved; no reset, clean, or stash was used. |
| Phase 10 | `establish-platform-observability` complete and strict-valid, active and not archived. Required dependency evidence: `docs/observability/phase-10-verification.md`. |
| Other maturity changes | `harden-platform-security`, `unify-course-authoring-experience`, and `establish-platform-maturity-foundation` complete but active/not archived. Several older unrelated changes remain active; see `openspec list`. |
| Baselines | Backend 278, Angular 308, Playwright 23 passing. |
| Logging/metrics | Structured redacted logs, request/correlation IDs, protected process-local metrics, and security/Course Studio signals from Phase 10. |
| Health | Public minimal `/health/live`; database-aware `/health/ready`; protected `/internal/metrics`. |
| Startup/migrations | `backend/start.sh` automatically ran `alembic upgrade head`, then Uvicorn. No separation or head gate. |
| Production config | JWT required, but database/origin/upload settings had development fallbacks; no centralized production validator. `.env` was loaded by database/migrations. |
| Host/proxy | No trusted-host middleware. Rate limiting used the socket peer and ignored forwarding headers, but server launch did not explicitly disable implicit proxy handling. |
| Deployment | Development Docker Compose, backend Dockerfile, CI migration/tests, and a `latest` container tag; no immutable release procedure. |
| Persistent state | PostgreSQL volume plus local `storybook`, `colorings`, and `badges` upload paths. Angular static output is rebuildable. MinIO is present in Compose but unused by application code. |
| Backup/restore | No tooling, schedule, integrity manifest, restore drill, RPO, or RTO. |
| Shutdown/workers | Uvicorn defaults; no application resource-disposal hook. No real queue, scheduler, or worker architecture. |
| CI | PostgreSQL migration, backend tests, Angular tests; separate container build workflow. |

The baseline is observational. Canonical Phase 11 behavior is in the documents linked from [README](../../README.md).
