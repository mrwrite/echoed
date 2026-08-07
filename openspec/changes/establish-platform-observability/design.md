## Context

Phase 7 introduced basic request IDs, request timing logs, and liveness/readiness. Phase 8 added privacy-safe security events, fixed-window rate limiting, hardened uploads, and the completed Course Studio added critical draft/review/publish workflows. The backend is a single FastAPI/Uvicorn process using SQLAlchemy; Angular is a bearer-token SPA; no job runner, metrics scraper, tracing backend, or commercial monitoring vendor is selected. Current logs are human strings with embedded key/value fields, raw paths are logged, exceptions are not centrally categorized into safe client responses, metrics are absent, and frontend components sometimes log raw error objects.

The change must remain deployable in the current architecture, preserve all security boundaries, avoid new high-cardinality or personal-data surfaces, and keep durable audit history separate. Local measurements and process-local metrics cannot establish production-scale guarantees.

## Goals / Non-Goals

**Goals:**

- Emit consistent JSON or developer-readable backend events with stable names, safe context, centralized redaction, and environment validation.
- Give every request a canonical safe request ID (accepting only a bounded safe upstream value, otherwise generating one), preserve a separate sanitized correlation hint, normalize route templates, and return safe diagnostic references.
- Count and time HTTP, authentication, authorization, throttling, upload, database, and Course Studio outcomes with bounded labels and a vendor-neutral Prometheus text export.
- Keep liveness process-only and readiness dependency-aware, bounded, machine-readable, and non-disclosing.
- Make Angular failures safely correlatable through response request IDs while retaining accessible messages and user work.
- Supply operational and incident guidance plus measured local overhead.

**Non-Goals:**

- Durable/append-only audit storage, SIEM, commercial monitoring, a distributed tracing backend, a queue/job framework, cloud/network architecture, business or learner analytics, distributed rate limiting, authentication redesign, or unrelated authoring/product expansion.

## Decisions

1. **One observability module owns configuration, redaction, structured events, and metrics.** `app.observability` will use the standard library to avoid a monitoring-vendor dependency. It exposes small `emit_event`, metric, context, and export primitives. Existing `app.log.logger` remains the application logger but receives the configured formatter/filter. Alternative: add Prometheus/OpenTelemetry packages. Rejected for this phase because a bounded single-process foundation does not need an external SDK, and the deployment/export backend is not selected.

2. **The server establishes a bounded safe request ID.** A caller/upstream `X-Request-ID` is accepted only when it matches the strict safe alphabet and length contract; absent or invalid values are replaced with a generated UUID. A separately sanitized, length-bounded `X-Correlation-ID` hint may be accepted and returned. Context variables make both values available to logs and internal code, and are reset after the request. Neither identifier is trusted for identity or authorization, and request IDs remain distinct from trace IDs; no W3C trace context is claimed.

3. **Middleware owns HTTP lifecycle instrumentation and safe unexpected responses.** It increments active requests, records method, normalized route template, status family, duration, actor classification, and safe organization presence. Raw query strings, bodies, user agents, and resource IDs never become metric labels. Known HTTP/validation responses retain framework semantics; unexpected exceptions become a generic JSON 500 containing only a message and request reference, while server logs retain the stack trace in a single `request.unhandled_exception` event.

4. **Metrics are in-memory and low-cardinality.** A locked counter/histogram registry emits Prometheus text without exemplars or IDs. Stable allowlisted labels include route template, method, status family/outcome, role category, limiter group, upload category, Course Studio operation, and database operation/result. The process-local reset/restart/multi-worker limitation is explicit.

5. **Metrics export is disabled by default and token-protected when enabled.** `METRICS_ENABLED` controls collection; `METRICS_ENDPOINT_ENABLED` controls `/internal/metrics`. Enabling the endpoint requires a non-empty `METRICS_ACCESS_TOKEN`; clients provide it in `X-Metrics-Token`. A disabled endpoint is concealed as 404 and unauthorized access returns 403 without endpoint data. Alternative: platform-admin bearer access. Rejected because scraper access is operational, not a user-management permission, and would couple infrastructure scraping to an interactive account/JWT.

6. **Health checks stay public but minimal.** Liveness never probes dependencies. Readiness performs `SELECT 1` using the existing engine, measures a bounded operation, and returns only overall status and a generic dependency state; failure is 503 and emits/records a database failure without host/database/exception text. Storage paths are not treated as mandatory readiness dependencies because current public static mounts create directories at startup and no independent storage service exists.

7. **Database observability wraps real boundaries, not SQL statements.** `get_db` logs/metrics session rollback/operation failures without SQL text or bound values. Readiness instruments connection failure. SQL echo remains off. Slow-query tracing and pool hooks are deferred until real production pool/deployment parameters are selected.

8. **Course Studio emits high-level operational events at API boundaries.** Import validation, draft creation/save/conflict, preview failure, review transitions, publish attempt/success/failure, and restore/duplicate/template operations use safe IDs in logs but only bounded operation/result labels in metrics. Course graphs, lesson content, assessment responses, feedback text, and imported documents are excluded. Frontend autosave/publish failures retain drafts and capture only safe status/reference/operation metadata locally.

9. **Frontend diagnostics remain local and privacy-safe.** A shared service extracts `X-Request-ID`, stores the most recent safe reference, and produces a copyable suffix only for unexpected server failures. A global Angular `ErrorHandler` records stable categories and sanitized metadata to the developer console without raw error objects, tokens, request bodies, course content, or stack traces for normal users. Lazy-chunk recovery remains the user-facing behavior.

10. **Security logs integrate; audit remains separate.** Phase 8 events call the same structured emitter and metrics primitives. Operational records may be rotated, sampled, or lost and do not promise retention/tamper resistance. `implement-platform-audit-events` owns persistence, append-only semantics, before/after state, access control, retention, export, search, and administrative review.

## Risks / Trade-offs

- **[Process-local metrics reset and diverge across workers]** → Document single-process semantics and require scraper-side aggregation/shared instrumentation in a later deployment change.
- **[Structured context could leak identifiers or secrets]** → Central redaction, allowlisted fields/labels, no bodies/queries, and regression tests for nested structures and header/token patterns.
- **[Authorization denial logs become noisy]** → Emit stable warning-level outcomes without target contents and aggregate metrics by scope/reason category, not ID.
- **[Metrics token is another secret]** → Endpoint disabled by default, fail configuration when exposure lacks a token, compare using constant-time logic, never log the token.
- **[Middleware cannot know route/actor until request processing]** → Resolve the route template after `call_next`; auth dependencies attach safe actor role/org context to request state when available.
- **[Catching unhandled exceptions could alter tests/behavior]** → Preserve known FastAPI errors, return the standard safe 500 status, attach request headers, and add focused regression tests before full suites.
- **[Instrumentation adds latency]** → Use lock-bounded in-memory updates, avoid payload serialization, and measure representative health/auth/course operations locally with metrics on/off.
- **[Low disk space destabilizes verification]** → Keep artifacts textual/small, avoid new packages, clean only generated outputs, and report any incomplete full-suite result rather than fabricating success.

## Migration Plan

1. Add the observability primitives and configuration with safe development defaults; no schema migration.
2. Replace request middleware/log formatting while preserving response security headers and existing request-ID compatibility.
3. Integrate security, database, upload, auth/authz, rate-limit, and Course Studio events incrementally with tests.
4. Add the disabled-by-default protected metrics endpoint and deployment-neutral documentation.
5. Add Angular reference handling/global diagnostics and focused tests.
6. Run full suites/build/audits, measure local overhead, then deploy with metrics endpoint disabled until an operator supplies a token and private access path.
7. Rollback is code/config rollback; no persistent observability schema or data migration exists.

## Open Questions

- Which production scraper/log collector and retention targets will be approved remains deployment work.
- Which routes warrant slow-operation alerts depends on production latency baselines; this phase provides configurable thresholds and local measurements only.
- Durable security action completeness, retention, tamper resistance, and operator search remain intentionally unresolved for `implement-platform-audit-events`.
