# Deployment Runbook

## Release gates

1. Identify the immutable commit/image digest and retain the prior known-good artifact and reviewed non-secret configuration.
2. Review schema compatibility and migration files. For destructive/irreversible work, stop until a tested backup/restore and explicit approval exist.
3. Verify encrypted off-host database and upload backups and record integrity evidence.
4. Supply the target environment configuration and run `python -m scripts.validate_operational_config` from `backend`.
5. Check database/storage reachability and capacity using provider tooling; never print a connection URL.
6. Run `bash migrate.sh` exactly once as a controlled release job. It validates, runs `alembic upgrade heads`, and verifies current heads. Application instances do not migrate.
7. Deploy the immutable artifact. `start.sh` validates again and launches Uvicorn with implicit proxy headers disabled and bounded graceful shutdown.
8. Poll `/health/live` for process startup, then `/health/ready` for database serviceability. Run `python -m scripts.verify_deployment --base-url <origin>` from an authorized network path.
9. Exercise safe public/authenticated smoke paths appropriate to the release without mutating production data unnecessarily.
10. Observe request/error/latency/readiness/auth/rate-limit signals for at least 15 minutes (longer for high-risk schema changes). Close the release only when alerts remain below policy thresholds.

Any failed gate stops promotion. Readiness failure removes/keeps the instance out of service; liveness failure permits restart. Do not restart-loop a configuration or migration failure.

Docker Compose is a development reference. It now runs a one-shot migration service before backend startup, waits for PostgreSQL health, and uses readiness plus a 35-second stop grace period. Its default credentials and bind mounts are not a production manifest. The container workflow publishes a commit-SHA tag for rollback provenance and also updates `latest`; deploy by SHA/digest, never by mutable tag alone.
