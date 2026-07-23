# Observability Baseline

Date: 2026-07-23

## Current state

| Area | Status | Evidence |
| --- | --- | --- |
| Backend logging | Implemented, basic | `backend/app/log.py` configures level and timestamp/name/level/message. Phase 7 request logs use stable key/value fields. |
| Request correlation | Implemented in Phase 7 | Middleware accepts a safe 1–128-character `X-Request-ID` or generates a UUID, exposes it on request state/response, and logs it. |
| Sensitive-log redaction | Partial | Raw tokens, decoded claims, and ORM users were removed from auth logs. No central redaction processor or regression scanner exists. |
| Frontend error handling | Partial | HTTP services and shared state panels handle expected failures; Phase 7 adds recoverable lazy-chunk navigation failure. No centralized exception reporting exists. |
| Liveness | Implemented in Phase 7 | `/health/live` proves process request handling. |
| Readiness/database check | Implemented in Phase 7 | `/health/ready` executes `SELECT 1` and returns 503 without database details on failure. |
| Metrics | Missing | No Prometheus/OpenTelemetry/custom metrics endpoint or SLI definitions. |
| Tracing | Missing | No trace context propagation or spans. Request ID is correlation, not tracing. |
| Error reporting | Missing | Exceptions reach logs; no aggregation, alert, ownership, or incident linkage. |
| Background task visibility | Not currently applicable/partial | No durable application job runner exists; generation-run rows are metadata, not an executing queue. |
| Authentication failure logs | Partial | Privacy-safe failure categories exist; no actor/IP aggregation or rate-limit event. |
| Authorization denial logs | Missing | `require_roles`/`require_org_roles` return 403 without a structured denial event. |
| Publishing/admin action logs | Missing | No durable audit or structured event instrumentation. |

## Before beta

- Define request/error/latency and database-readiness SLIs with bounded label cardinality.
- Log authorization denial category and protected resource type without tokens, learner content, or unnecessary personal identifiers.
- Establish exception ownership and alert routing using an approved deployment-compatible mechanism.
- Add privacy-redaction tests and a log retention/access policy.
- Instrument publishing, privilege, access-grant, invitation, and destructive actions through the future audit-event service.

## Before general availability

- Adopt vendor-neutral trace/metric interfaces, then bind them to the selected infrastructure.
- Propagate trace/request context across frontend, API, database, and future background jobs.
- Define dashboards, alert thresholds, on-call ownership, incident review, and availability/error-budget policy.
- Measure notification/search/job backlogs if those systems are introduced.

## Separate OpenSpec work

`establish-platform-observability` owns metrics, tracing, error aggregation, redaction contracts, and operator runbooks. `implement-platform-audit-events` owns durable actor/action/resource history. Phase 7 intentionally adds no commercial monitoring dependency.
