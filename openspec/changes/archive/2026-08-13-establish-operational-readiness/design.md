## Context

EchoEd is a FastAPI/SQLAlchemy backend and Angular SPA currently launched directly or with Docker Compose. Phase 10 supplies structured logs, request correlation, health/readiness, and process-local metrics, but operational behavior remains implicit: `start.sh` automatically upgrades the database, database and URL settings have development fallbacks, forwarded-header trust is not defined, uploads use local bind-mounted directories, and no repository tooling proves backup/restore or release drills. The current architecture has no worker queue, distributed metrics/rate-limit state, object-storage provider, or selected production hosting platform.

This design treats operations as a contract at the application and repository boundary. It supplies fail-closed validation and deterministic, locally verifiable tools while leaving provider-specific deployment, scheduling, secret storage, backup destinations, and alert delivery to an operator-selected environment.

## Goals / Non-Goals

**Goals:**

- Reject unsafe production configuration before application modules initialize or traffic is served, without disclosing values.
- Enforce allowed hosts and make forwarded metadata authoritative only for explicitly trusted network peers.
- Separate migration execution from normal process startup and codify preflight, readiness, smoke, rollback, and shutdown gates.
- Reuse Phase 10 health, metrics, and structured events for pragmatic SLOs and alerts.
- Identify all persistent state and provide safe backup/restore/integrity tooling plus repeatable non-production operational drills.
- Define defensible initial RPO/RTO targets, storage ownership, environment separation, secret rotation, escalation, and truthful limitations.

**Non-Goals:**

- Durable platform audit events, distributed rate limiting/state, identity redesign, new hosting/cloud/reverse-proxy/object-storage infrastructure, distributed tracing or telemetry expansion, application features, or claims of provider-independent disaster recovery.

## Decisions

1. **A standard-library operational settings module validates before application imports.** `app.operational_config` parses environment identity and the security-sensitive runtime contract without importing database, authentication, or route modules. `app.main` loads it first, and a CLI preflight uses the same validator. Production requires explicit database, secret, origin/URL, host, release, storage, migration, and observability decisions and rejects known development defaults. Errors report setting/category names only. Alternative: rely on Pydantic settings scattered across modules. Rejected because current settings are distributed and importing them can already create the engine.

2. **Development/test keep explicit safe local defaults; production has none.** `APP_ENV` is read before optional dotenv loading. A production process never imports values from a checked-in/local `.env`; every required production value must be in its process environment. Alternative: load dotenv in all environments. Rejected because an image includes repository files and could silently inherit development secrets.

3. **Host validation is ASGI-enforced and proxy trust is peer-based.** Starlette's trusted-host middleware rejects unexpected `Host` values. A small network-context resolver accepts `X-Forwarded-For`, `X-Forwarded-Proto`, and `X-Forwarded-Host` only when proxy trust is enabled and the direct socket peer matches an explicit IP/CIDR allowlist. Startup disables Uvicorn's implicit proxy-header processing so untrusted metadata cannot be applied before application checks. Alternative: trust all forwarded headers behind an assumed proxy. Rejected because no production topology is selected.

4. **Migrations are an explicit release step.** Normal application startup validates configuration but never mutates schema. An explicit migration command performs validation and `alembic upgrade heads`; post-migration verification compares current heads with repository heads. Risky/irreversible changes require an operator-approved backup and compatibility plan. Alternative: retain automatic startup migration. Rejected because multiple instances can race and failed migrations blur release and process health.

5. **Lifecycle hooks expose bounded drain diagnostics and release resources.** Uvicorn is configured with a finite graceful-shutdown timeout; on ASGI shutdown EchoEd records lifecycle events and disposes the SQLAlchemy engine. Actual HTTP acceptance/draining remains the server's responsibility. With no worker framework, no invented job-drain protocol is added.

6. **Release validation is deployment-neutral automation.** A Python operational CLI validates config, database connectivity/migration state, health endpoints, and safe drill workflows. Container Compose remains a development reference but gains health ordering, explicit migration invocation, immutable release guidance, and shutdown bounds. Alternative: add Kubernetes/cloud manifests. Rejected as an unsupported infrastructure decision.

7. **Backup tooling proves format, integrity, restore, and storage recovery using safe data.** Repository tooling supports deterministic SQLite plus filesystem-asset drill bundles with a versioned manifest and SHA-256 checksums. Production PostgreSQL uses documented native logical/managed backups and the same verification principles; the repository does not pretend a SQLite copier backs up PostgreSQL. Configuration is reproducible from versioned non-secret templates; secrets are backed up only by the operator's secret manager. Static Angular assets are rebuilt, while user-upload directories and the database are persistent sources of truth.

8. **Initial objectives are conditional operational targets.** Availability, successful-request rate, server-error rate, latency, and readiness are defined over a rolling 30-day window with alert conditions using Phase 10 signals. The initial recovery targets are RPO 24 hours and RTO 4 hours, conditional on daily encrypted off-host database/upload backups and a measured restore drill. Process-local metrics cannot calculate fleet-wide compliance; external aggregation/alert delivery remains required.

9. **Drills are executable, isolated, and evidence-producing.** A test/drill module uses temporary directories, a disposable SQLite database, local ASGI/Uvicorn lifecycle control, and synthetic configuration. It never targets production and reports pass/fail facts without secret values. Documentation records prerequisites, commands, expected/observed behavior, and limitations.

10. **Rollback is three distinct operations.** Application rollback redeploys a previous immutable artifact; configuration rollback restores a reviewed previous non-secret configuration and matching secrets; database rollback is never assumed and requires a verified downgrade or backup restore. Compatibility gates decide when artifact-only rollback is safe.

## Risks / Trade-offs

- **[Strict production validation can reject previously tolerated deployments]** -> Document every required setting, provide a validation-only command, and retain development/test defaults.
- **[Application parsing cannot secure headers already rewritten by the server]** -> Launch Uvicorn with implicit proxy processing disabled and document explicit network topology requirements.
- **[Local filesystem uploads can disappear with an ephemeral container]** -> Require an explicit persistence acknowledgement and absolute storage paths in production; document external object storage as deferred infrastructure.
- **[Repository backup tooling could be mistaken for a PostgreSQL backup solution]** -> Refuse unsupported database schemes and clearly separate the safe local drill from production-native backup commands.
- **[Process-local metrics cannot establish fleet SLOs or deliver alerts]** -> Label objectives as targets, document aggregation limitations, and never claim external notification wiring.
- **[A schema change can make code rollback unsafe]** -> Require expand/contract compatibility or an approved restore/downgrade plan before migration.
- **[Shutdown tests cannot reproduce every platform signal behavior]** -> Verify the ASGI/Uvicorn lifecycle and resource cleanup deterministically, then require platform-specific termination drills after a host is selected.

## Migration Plan

1. Deploy the validator and run it against a staged production-equivalent environment without starting the API.
2. Create encrypted, off-host backups and verify integrity before changing startup/migration behavior.
3. Run explicit Alembic migration and head verification as a single controlled release step.
4. Deploy an immutable application artifact with automatic migrations disabled and implicit proxy headers disabled.
5. Verify liveness, then readiness, smoke checks, metrics/log signals, and a bounded monitoring period.
6. On failure, decide separately whether to roll back application, configuration, or restore/downgrade the database based on schema compatibility.
7. Retain the previous known-good artifact and reviewed configuration until the monitoring gate closes.

## Open Questions

- The hosting platform, reverse-proxy addresses, external metrics/log aggregation, alert-delivery provider, backup scheduler/destination, encryption key custody, and object-storage destination remain operator/infrastructure decisions.
- Production RPO/RTO must be re-measured against the selected managed database, data volume, and storage system before a production commitment.
- Durable, searchable, tamper-resistant security history remains owned by `implement-platform-audit-events`.
