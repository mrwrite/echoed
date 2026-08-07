# Incident Observability Guide

This is focused incident-readiness guidance, not a complete incident-response program. Preserve request IDs, stable events, aggregate metrics, UTC time windows, deployed commit/config version, and operator actions. Never preserve secrets or unnecessary learner/course content.

| Scenario | Detection and evidence | Immediate containment | Escalate when |
| --- | --- | --- | --- |
| Elevated login failures | `echoed_authentication_total` failure ratio, `auth.login.failed`, limiter triggers | Confirm service/readiness; check broad category/config changes without account enumeration | Sustained increase, suspected credential attack, or legitimate users broadly blocked |
| Elevated 500s | HTTP status-family/request-failure metrics and `request.unhandled_exception` by normalized route/request ID | Remove unready instances; pause a failing high-impact action if normal controls permit | Error ratio persists, data integrity may be affected, or multiple roles/workflows fail |
| Database unavailable | Readiness `503`, database failure/outcome/duration | Stop routing to unready instances; verify database service through approved tools; avoid retry storms | Outage exceeds operational objective, recovery risks data, or all instances are unready |
| Unexpected throttling | Limiter-group triggers and `rate_limit.triggered` | Verify environment limits and per-process topology; do not disable auth protection casually | Legitimate flow is blocked broadly or abuse bypass/distributed inconsistency is suspected |
| Cross-org denials | Authorization denial scope/reason aggregates and correlated request IDs | Confirm tenant boundary remains closed; preserve actor/target metadata only from authorized logs | Pattern suggests probing, a permitted request is denied, or any cross-org data exposure is suspected |
| Upload failures | Upload result/duration and rejection codes | Keep validation enabled; verify size/type/store availability | Valid uploads broadly fail or content execution/unauthorized access is suspected |
| Studio save conflicts | Course Studio conflict outcomes and request references | Preserve local work; use documented reload/recovered-copy path; avoid overwriting server state | Conflicts become systemic or published-version isolation is questioned |
| Publishing failures | Publish attempt/blocked/success and HTTP failures | Keep current learner availability unchanged; resolve validation/dependency cause | State appears partially published or learners see unapproved content |
| Worker failures | Not applicable: no executing worker exists | Do not infer queue health from generation-run metadata | A worker is introduced without lifecycle instrumentation |

For suspected data exposure or privilege compromise, prioritize containment and preservation over diagnostic verbosity. Use the security escalation process; operational logs are not a tamper-resistant audit ledger.

Phase 11 release containment, application/configuration/database rollback boundaries, recovery ownership, and alert thresholds are defined in the [deployment runbook](deployment-runbook.md), [migration and rollback policy](migration-and-rollback-policy.md), [alerting policy](alerting-and-escalation.md), and [backup/restore procedure](backup-and-restore.md). Do not attempt an application-only rollback when schema compatibility is unknown.
