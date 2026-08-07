# Phase 10 Observability Baseline

Date: 2026-08-07

This baseline records the repository before Phase 10 runtime changes. It is an implementation audit, not a production-readiness or monitoring-coverage claim.

## Repository and OpenSpec state

- Branch: `aqw-echoed-dev`
- Commit: `c6336fa79458c08da75746954615a86522e766a8`
- Dirty tree: extensive expected, uncommitted Phase 8 security-hardening and unified Course Studio work is present. Phase 10 preserves all of it. Other older active OpenSpec changes also exist; no archived history is modified.
- `harden-platform-security`: complete, 30/30 tasks, strictly valid, active and not archived.
- `establish-platform-maturity-foundation`: complete, 21/21 tasks, active and not archived.
- `unify-course-authoring-experience`: complete, 58/58 tasks, active and not archived.
- Most-recent verified baselines: 269 backend tests, 299 Angular tests, 22 Playwright tests, passing production Angular build, zero production npm vulnerabilities, strict Phase 8 validation, and clean `git diff --check` apart from line-ending notices.

## Existing observability architecture

- Backend logging: `backend/app/log.py` uses Python `logging.basicConfig` with environment-selected level and human-readable timestamp/name/level/message output. Event data is embedded in format strings rather than emitted as structured records. Invalid log levels silently become `INFO`.
- HTTP middleware: `backend/app/main.py` times every request, accepts a 1–128 character safe `X-Request-ID` or generates a UUID, stores it on `request.state`, returns it as `X-Request-ID`, writes completion/failure logs, and adds baseline security headers. It logs raw URL paths rather than normalized route templates.
- Correlation: request ID is the only correlation value. It is available to handlers and Phase 8 security events but is not distinct from a caller correlation hint or distributed trace ID. No internal HTTP service client or request-spawned background worker currently needs propagation.
- Security events: Phase 8 `security_event` writes privacy-aware key/value messages for authentication denial, rate limiting, role/user changes, final-admin protection, invitations, upload rejection, and forum moderation. These are ephemeral operational logs, not durable audit records.
- Error handling: middleware logs unexpected exceptions and lets framework handling produce the response. Known HTTP/validation errors are not categorized centrally; request IDs are not consistently included in safe error bodies; database/dependency failures have limited stable event names.
- Health: `/health/live` returns process liveness. `/health/ready` executes bounded `SELECT 1`, returns 503 with a generic database message on SQLAlchemy errors, and currently includes the public dependency name/status on success.
- Metrics: none. There is no counter, histogram, active-request gauge, export endpoint, or cardinality policy.
- Database: SQLAlchemy engine/session setup has no failure/rollback instrumentation; unrestricted SQL echo is not enabled. SQLite is used in tests and disposable verification; deployment documentation assumes PostgreSQL and one Uvicorn process.
- Background work: no Celery/RQ/worker/scheduler or application-executed queue exists. Generation-run rows contain product metadata but are not a worker implementation.
- Course Studio: draft/autosave/conflict/import/preview/review/publish/restore workflows have domain behavior and tests but no unified operational events or metrics. Frontend failures use local lifecycle messages.
- Angular diagnostics: expected security status messages and lazy-chunk recovery exist. Several components log raw error objects to the browser console; there is no global privacy-safe error handler or shared request-reference extraction.
- Deployment assumptions: one API process, direct-peer rate limiting, no trusted forwarded headers, vendor-neutral logs written to process output, no selected metrics scraper or commercial monitoring service.
- Rate limiter: locked, process-local fixed windows configured by environment; triggers call Phase 8 security logging and return `429`/`Retry-After`, but no operational metrics exist.

## Baseline risks and constraints

- Raw exception objects or console logs may contain more context than policy permits.
- Raw request paths can create cardinality and privacy problems; raw queries/bodies must never be logged globally.
- Request IDs are useful but are not trace IDs and caller-provided values require stricter conceptual separation.
- Public metrics would reveal internal traffic/security posture; any export must be disabled by default or explicitly protected.
- Database errors, Course Studio lifecycle failures, and authorization denials cannot yet be reliably aggregated by stable event name.
- Drive C began this phase critically low on free space. Only recoverable unused Playwright browser caches were removed; source, databases, uploads, and user work were untouched. Verification must continue to clean generated artifacts and report environmental limitations accurately.
