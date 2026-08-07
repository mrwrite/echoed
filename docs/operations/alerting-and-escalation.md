# Alerting, Ownership, and Escalation

The application exposes signals; no external notification provider or on-call routing is wired. The deploying organization must assign the named owner roles and connect collection before claiming alert coverage.

| Condition | Severity / trigger | Owner and response | Escalation / runbook |
| --- | --- | --- | --- |
| Liveness unavailable | Critical; 2 consecutive checks | Platform operator: stop promotion/restart once, inspect lifecycle/config logs | Engineering incident lead; deployment runbook |
| Readiness/database unavailable | Critical; 2 minutes | Database/operator owner: remove traffic, verify dependency and recent migration | Incident lead + database owner; Phase 10 incident guide |
| 5xx rate | High; >2% for 5 minutes or any sharp release-correlated rise | Application operator: correlate request IDs, halt/rollback release if safe | Backend owner; observability runbook |
| p95 latency | Medium; >1 second for 15 minutes | Backend owner: inspect slow routes/database signals | Incident lead if user impact grows |
| Login failures | Medium; 3x comparable baseline for 10 minutes | Security responder: distinguish attack, outage, or release regression | Security owner; incident guide |
| Rate-limit triggers | Medium; sustained unexpected triggers for 10 minutes | Security/application owner: inspect limiter category/process count | Security owner; never disable blindly |
| Backup missed/failed | Critical; no verified daily backup by next window | Data owner: stop risky deploys and repair backup path | Incident lead; backup/restore runbook |
| Restore drill failed | Critical readiness blocker | Data owner: preserve evidence, correct before production claim | Engineering lead |
| Disk/storage write rejection | High; repeated upload failures or capacity alert | Storage owner: contain uploads, inspect persistence/capacity | Incident lead; storage section |

External aggregation, paging, schedules, contact lists, maintenance-window suppression, and escalation timers remain infrastructure/organizational dependencies.
