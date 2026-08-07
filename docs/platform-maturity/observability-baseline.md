# Observability Baseline

Date: 2026-08-07 (Phase 10 update)

| Area | Current state | Evidence / boundary |
| --- | --- | --- |
| Backend logging | Foundation implemented | Stable structured events, JSON/developer format, request context, normalized routes, and environment validation. |
| Request correlation | Implemented | Safe request IDs plus a separate bounded correlation hint are returned and propagated through request context. |
| Redaction | Foundation implemented | Central recursive sensitive-key/token/binary redaction and regression tests; call sites must still omit private content. |
| Frontend errors | Foundation implemented | Metadata-only HTTP/global/lazy-chunk diagnostics, safe support references, and accessible existing messages. |
| Liveness/readiness | Implemented | Process liveness is independent of database-backed readiness; responses omit infrastructure details. |
| Metrics | Foundation implemented | Locked process-local bounded metrics; optional token-protected Prometheus text export is disabled by default. |
| Database | Partial | Session/readiness failures and duration are observable without SQL/values; no per-query tracing or pool metrics. |
| Authentication/authorization | Implemented operationally | Stable outcome/denial events and bounded counters without account or protected target labels. |
| Course Studio | Implemented operationally | Draft, conflict, preview, review, duplicate/template/import, and publish boundary events; course content is excluded. |
| Background work | Not currently applicable | No executing worker, scheduler, broker, or queue exists. Generation-run rows are metadata only. |
| Tracing/aggregation/alerting | Deferred | Request correlation is not distributed tracing; no collector, dashboards, or alert ownership is selected. |

## Remaining production work

The recommended next change, `establish-operational-readiness`, should bind these vendor-neutral signals to a selected deployment, configure collection/retention/alerts, validate multi-process scraping, and rehearse failure operations. Local metrics reset at process restart and require external aggregation in a multi-process deployment.

`implement-platform-audit-events` remains separate. It owns append-only persistence, atomic action/event semantics, actor/action/target/organization, minimized before/after security state, retention, restricted search/export, privacy, administrative review, and tamper resistance. Operational logs are potentially ephemeral diagnostic records and cannot satisfy that contract.
