# Current Observability Audit

Date: 2026-08-07

This audit separates ephemeral operational diagnostics from durable security audit records. Frontend controls are not security controls, and observability does not authorize an action.

| Area | Before Phase 10 | Missing visibility / privacy risk | Phase 10 disposition | Signal class |
| --- | --- | --- | --- | --- |
| Python logging | Basic text logger and Phase 8 key/value security messages | No common schema or central nested redaction | Central structured formatter, stable events, recursive redaction | Logs |
| FastAPI requests | Timing and request ID, raw paths | Unnormalized routes and inconsistent error categories | Route-template request count/duration/status plus bounded context | Logs, metrics |
| Exceptions | Framework handling plus request failure log | Unsafe client detail was possible outside known HTTP errors | Generic `500` with request reference; server-side categorized event | Logs, metrics |
| Security events | Privacy-aware but text-oriented and ephemeral | Hard to aggregate; not durable | Routed through structured logging and bounded counters | Logs, metrics; not audit ledger |
| SQLAlchemy | No SQL echo, but few stable failure signals | Session/readiness failures difficult to aggregate | Rollback plus `database.operation_failed` and duration/outcome metrics | Logs, metrics, health |
| Health | Process live and database ready checks | Policy and exposure were not canonical | Separate minimal liveness/readiness contracts | Health |
| Metrics | None | No vendor-neutral aggregate operational signal | In-process bounded registry and protected Prometheus text export | Metrics |
| Authentication | Phase 8 security failures | No success/attempt aggregate | Attempt/success/failure/throttle counters and stable events | Logs, metrics |
| Authorization | Selected Phase 8 events | Inconsistent platform/org denial aggregation | Platform/org reason categories without target data | Logs, metrics |
| Rate limiting | Process-local enforcement and security event | No aggregate limiter-category count | Bounded trigger counter | Logs, metrics |
| Uploads | Hardened validation and rejection events | Attempts/success/duration absent | Category/outcome metrics and rejection diagnostics, no filenames/bytes | Logs, metrics |
| Course Studio | User messages and domain state | Draft, conflict, preview, review, publish outcomes not aggregated | High-level events/counters; content graphs remain excluded | Logs, metrics |
| Angular | Expected status messages and lazy-chunk recovery | Raw errors could reach console; no request-reference helper | Metadata-only diagnostic service, interceptor, global handler, safe references | Browser diagnostics |
| Background work | No executing worker/queue; generation-run rows are metadata | No worker lifecycle to instrument | Fact documented; future workers must adopt the event contract | Logs/metrics when introduced |
| CI/deployment | Tests/builds and container health checks | No external collector, alert routing, or production topology | Vendor-neutral process output/endpoints and operator guidance only | Diagnostics |

## Dependency and deployment findings

The implementation uses Python and Angular platform facilities already present. No monitoring SDK, commercial agent, job framework, or tracing backend was added. Production documentation currently assumes process stdout, a required SQL database, and potentially multiple API processes in the future; the metrics and rate-limit stores remain per-process. Trusted-proxy and hosting topology are deliberately not invented here.

## Durable audit boundary

Operational logs are potentially ephemeral, mutable through retention systems, and optimized for diagnosis. `implement-platform-audit-events` remains responsible for append-oriented persistence, retention, restricted search/export, before/after security state, tamper resistance, and administrative review.
