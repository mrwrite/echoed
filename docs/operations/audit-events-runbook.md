# Audit Events Runbook

## Review and correlation

- Platform administrators use `/admin/audit-events` or `GET /api/audit-events`.
- Active organization administrators use `GET /api/orgs/{org_id}/audit-events` with the matching `X-Org-Id` context.
- Correlate an event's safe request ID with structured logs. Never request tokens, cookies, passwords, private content, or full database rows from users.
- Export is limited, authorization-scoped, formula-safe CSV and creates its own durable event.

## Integrity verification

From `backend/`:

```powershell
venv\Scripts\python.exe scripts\manage_audit_events.py verify
venv\Scripts\python.exe scripts\manage_audit_events.py verify --organization-id ORGANIZATION_UUID
```

Success reports only scope and checked count. Failure is an incident signal: stop retention, preserve database/backups/log correlation, restrict administrative writes if necessary, and escalate to the security owner. Do not repair hashes in place.

## Retention

Dry-run first:

```powershell
venv\Scripts\python.exe scripts\manage_audit_events.py retain --before 2025-08-13T00:00:00
```

Production application additionally requires `--apply --ack-production --backup-reference SAFE_REFERENCE`; a preservation hold always refuses deletion. Backup references must identify an operator-controlled encrypted backup without embedding a credential or URL secret.

## Backup and restore

The audit table and integrity fields are part of the primary database backup. Restore acceptance requires database-native integrity checks followed by audit-chain verification for the platform and known organization scopes. Never export audit CSV as a substitute for database backup. Preserve audit backups separately according to incident and retention policy.

## Known limitations

- Hash chains are not externally anchored and cannot defeat a database superuser.
- SQLite test concurrency does not establish PostgreSQL production contention behavior.
- No external audit archive, legal-hold service, or WORM target is configured.
