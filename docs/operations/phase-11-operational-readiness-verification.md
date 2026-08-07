# Phase 11 Operational Readiness Verification

Date: 2026-08-07

## Scope and baseline

- OpenSpec change: `establish-operational-readiness` (active, not archived).
- Starting branch/commit: `aqw-echoed-dev` / `c6336fa79458c08da75746954615a86522e766a8`.
- Starting tree: dirty with user-authored Phase 8, Course Studio, Phase 10, and unrelated active-change work. No reset, clean, checkout, or stash was used.
- Dependency: `establish-platform-observability` was complete and strict-valid but active/not archived. `harden-platform-security`, `unify-course-authoring-experience`, and `establish-platform-maturity-foundation` were also complete and active/not archived.
- Starting verified baselines: backend 278, Angular 308, Playwright 23.

## Implemented contract

- `app.operational_config` validates environment identity, PostgreSQL URL category, JWT policy, HTTPS origins/external URL, allowed hosts, explicit proxy peer CIDRs, release/deployment identity, storage persistence acknowledgement/paths, non-automatic migrations, structured logs, metrics, request diagnostics, and shutdown bounds. Production never loads dotenv.
- `scripts.validate_operational_config` provides a value-free validation-only gate. A synthetic valid production configuration returned success; replacing its host allowlist with `*` returned exit 2 and only `Operational configuration invalid: ALLOWED_HOSTS...`.
- Starlette trusted-host middleware rejects unexpected hosts. `network_trust` applies forwarded client/protocol/host data only when proxy trust is enabled and the direct peer matches an explicit IP/CIDR. Uvicorn starts with `--no-proxy-headers`; the rate limiter uses the resolved safe client address.
- Normal `start.sh` no longer migrates. `migrate.sh` validates, runs `alembic upgrade heads`, and verifies database heads; Docker Compose models it as a one-shot dependency and publishes health/shutdown configuration. The container workflow adds an immutable commit-SHA tag.
- FastAPI lifespan events cover application start and shutdown, mark draining state, and dispose the SQLAlchemy engine. Uvicorn and Compose have bounded, ordered shutdown settings.
- Safe development/test backup tooling creates a SQLite online backup plus uploaded-asset bundle, versioned manifest, byte counts, and SHA-256 integrity records; restore requires absent targets and rechecks database integrity. It rejects production/staging, path traversal, corruption, and unacknowledged data.
- Deployment, migrations/rollback, health/shutdown, SLOs, alerts/escalation, backup/restore, storage ownership, secret rotation, and drills have canonical operations documents. Phase 10 runbooks are cross-linked rather than duplicated.
- No dependency or database schema migration was added.

## Operational drills

Command: `backend/venv/Scripts/python.exe -m scripts.run_operational_drills` from `backend`.

| Drill | Result | Observed evidence |
| --- | --- | --- |
| Invalid production configuration | Pass, 0.09 ms | Unsafe wildcard host rejected without values. |
| Migration lifecycle | Pass, 546.93 ms | Repository head found; startup non-mutating; explicit upgrade and head-verification gates present. |
| Startup, health, database outage, shutdown | Pass, 776.07 ms | ASGI lifecycle completed; liveness stayed 200 while a deterministic synthetic database outage made readiness return generic 503; shutdown hooks ran. |
| Failed post-deploy | Pass, 230.89 ms | Unavailable readiness target stopped verification. |
| Backup/restore/rollback/storage recovery | Pass, 67.88 ms | Manifest and checksums verified; isolated database record and asset bytes restored to known-good state. |
| Secret/config rotation simulation | Pass, 0.93 ms | Old and replacement synthetic production configs validated independently; neither value was emitted. |

Targeted tests additionally verified valid/invalid production matrices, localhost/wildcard/HTTP/default rejection, trusted and spoofed forwarding metadata, allowed/rejected hosts, backup corruption/traversal/target safety, restored SQL usability, asset recovery, and database-engine disposal.

The Alembic history contains PostgreSQL-specific DDL. A disposable SQLite upgrade correctly cannot represent production migration execution. The local PostgreSQL service and Docker daemon were unavailable, and the critically full drive could not initialize a disposable PostgreSQL cluster. Therefore this evidence verifies the migration graph and release gates, while the existing PostgreSQL CI migration job and the production-equivalent pre-deploy rehearsal remain mandatory before a real deployment. No user database was touched.

## Recovery objectives and ownership

- Initial RPO: 24 hours, conditional on an operator actually scheduling daily encrypted, off-host PostgreSQL and upload backups.
- Initial RTO: 4 hours, conditional on available known-good artifacts/configuration, credentials, operators, and representative restore capacity.
- Local 67.88 ms recovery only proves small-fixture tooling correctness and does not validate production volume or the 4-hour target.
- PostgreSQL and uploaded assets are mutable backup state; Angular/backend artifacts are rebuilt; non-secret configuration is reproducible; secret values remain in an external secret manager.

## Automated verification

| Gate | Final result |
| --- | --- |
| Backend complete suite | **PASS — 299 passed**, 4169 existing deprecation warnings, 133.80 s. Baseline increased by 21 targeted tests, including both cross-version nested-route normalization representations. |
| Backend compile/static syntax | **PASS** — `compileall` over app, scripts, and tests. |
| Backend lint/format | Not configured in repository/venv; no pass claimed. |
| Angular complete suite | **PASS — 308 passed**. Final run used one build worker after an initial local Node memory failure. No baseline reduction. |
| Frontend lint/format | No lint/format scripts configured; no pass claimed. |
| Production Angular build | **PASS** — initial bundle 439.76 kB raw / 120.41 kB estimated transfer. |
| Playwright complete suite | **PASS — 23 passed**, 28.8 s, one Chromium worker. |
| Production dependency audit | **PASS — 0 vulnerabilities** from `npm audit --omit=dev`. |
| Docker Compose syntax | **PASS** — `docker compose -f docker-compose.yml config --quiet`. |
| Strict OpenSpec | **PASS** — `openspec validate establish-operational-readiness --strict`. |
| `git diff --check` | **PASS**; line-ending notices only. |

Phase 8/10 regressions are covered by the 299 backend, 308 Angular, and 23 Playwright suites, including forum fail-closed behavior, role/org boundaries, accessible throttling, safe references, health, metrics, redaction, uploads, and Course Studio behavior.

## Cleanup

Disposable API/Angular servers on ports 8000/4200 were stopped by exact listener PID. `phase11_playwright.db`, temporary logs, Playwright results/report, generated Angular `dist`, backup bundles, restored fixtures, and drill directories were removed. No real secrets or production data were used or committed.

## Known limitations and deferred work

- No hosting/reverse-proxy provider, external monitor/alert delivery, centralized logs/metrics, production backup scheduler/destination, or object-storage service is selected.
- SLO calculations and rate limiting remain process-local and cannot establish fleet compliance.
- Repository backup automation intentionally supports only acknowledged test SQLite/filesystem data; production PostgreSQL/provider backup and representative encrypted restore must be executed in the selected environment.
- Local upload paths remain a production durability risk unless mounted to operator-managed persistent storage; the validator requires acknowledgement but cannot prove the mount.
- JWT uses a single signing key; rotation invalidates existing tokens. Revocation/overlap is deferred identity work.
- No job/worker shutdown or recovery semantics exist because there is no worker architecture.
- Docker Compose is a development reference with development defaults, not a production manifest.
- Durable append-only/tamper-resistant administrative events remain exclusively assigned to `implement-platform-audit-events`.
- Distributed state/rate limiting, new hosting infrastructure, distributed tracing, authentication redesign, and application feature work remain out of scope.

## Recommended next change

Proceed with `implement-platform-audit-events` as the next application-owned platform-maturity change. Provider-specific deployment acceptance (real PostgreSQL migration, encrypted production-volume restore, proxy topology, external signal collection/alert delivery, and measured RPO/RTO) must be completed as an environment gate and must not be mislabeled as durable audit functionality.

This phase establishes a tested repository-level operational contract; it does not by itself claim EchoEd is production-ready.
