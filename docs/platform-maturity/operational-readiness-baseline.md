# Operational Readiness Baseline

Date: 2026-07-23

Status values: implemented, documented/unverified, missing, or blocked by hosting decision.

| Concern | Status | Evidence / required timing |
| --- | --- | --- |
| Local environment configuration | Implemented | `.env`, Angular environments, proxy config, Docker Compose, README. |
| Production configuration validation | Partial | `JWT_SECRET` fails fast; database URL has a development fallback and allowed origins default locally. The checked-in Angular production environment hard-codes the current Railway API, which blocked local production-configuration runtime measurement. Add validated deployment-time frontend configuration and an explicit backend production-mode validator before beta. |
| Database migrations | Implemented mechanism, documented/unverified operation | Alembic configuration and version history exist. No automated deploy gate or rollback rehearsal. Required before beta. |
| Seed behavior | Implemented for demo; production safeguard incomplete | `backend/scripts/reseed_demo.py` is deterministic and destructive by intent. It must never target production; add environment guard in operational proposal before beta. |
| Backup | Missing | Docker volume exists but is not a backup. Hosting/storage decision required before beta. |
| Restore | Missing | No tested restore runbook or recovery-time/recovery-point objective. Restore drill required before beta. |
| Disaster recovery | Blocked by hosting decision | No selected regions, failover, storage, or DNS architecture. Required before general availability. |
| Deployment | Documented only for local Compose | No production pipeline, artifact promotion, approval, or provenance process. Required before beta. |
| Rollback | Missing | Application, migration, and static-asset rollback procedure is unspecified. Required before beta. |
| Health verification | Implemented baseline in Phase 7 | Liveness and database readiness endpoints exist; deployment integration is hosting-specific. |
| Static assets/uploads | Partial | Angular assets are build artifacts; backend local directories are volume-mounted. Object storage ownership, backups, authorization, and lifecycle are unresolved. |
| Secret rotation | Missing | Environment secrets are supported, but no rotation/revocation process exists. Required before beta. |
| Local development | Implemented | README, architecture, proxy, Docker Compose, direct Python/Angular workflows. |
| Test environment | Implemented locally | SQLite fixtures, Karma ChromeHeadless, Playwright seeded demo. Ephemeral CI environment and artifact retention need verification. |
| Temporary QA cleanup | Implemented practice | Phase 6/7 use disposable DB/services and remove them. Automate in future readiness work. |
| Production data safeguards | Missing policy | No production seed guard, retention/deletion workflow, backup classification, or masked support copy process. Required before beta. |
| Scheduled jobs | Not implemented | No scheduler/job worker; future notification/export/search work must define ownership and visibility. |
| Dependency updates | Partial | Lockfiles exist; no automated advisory/update policy or cadence. Patched urgent Angular runtime manually in Phase 7. |

## Release staging

Before beta: choose hosting assumptions, validate production config, protect seed commands, establish deploy/rollback, complete a migration and backup/restore rehearsal, define secret rotation, wire health checks, and document data safeguards.

Before general availability: disaster-recovery targets and drill, capacity/load evidence, maintenance windows, incident ownership, dependency update SLA, and storage lifecycle must be approved.

`establish-operational-readiness` should own these actions. This audit does not invent a cloud provider, container orchestrator, managed database, or commercial service.
