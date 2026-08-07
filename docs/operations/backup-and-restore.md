# Backup, Restore, and Recovery

## Production policy

- PostgreSQL: daily encrypted logical or provider-native backup, plus provider-supported continuous recovery if selected. Retain 7 daily and 4 weekly recovery points; store in a separate failure domain/account with access logs and least privilege.
- Uploads: daily versioned backup of `STORYBOOK_PATH`, `COLORINGS_PATH`, and `BADGES_PATH`, coordinated closely enough with the database to preserve ownership references. Apply the same 7-daily/4-weekly retention.
- Configuration: version non-secret templates and immutable release metadata. Back up secrets only within the approved secret manager; never in repository bundles.
- Angular/static application assets: rebuild from the immutable release; they are not mutable backup state.
- Verify every artifact checksum/catalog after creation and run an isolated restore at least quarterly and after storage/schema changes.

Initial conditional targets are RPO 24 hours and RTO 4 hours. They depend on successfully scheduled daily off-host backups, available credentials/operators, compatible release artifacts, and a restore procedure measured with representative production volume. Local drill timings prove tooling behavior only and do not prove these production targets.

## Safe repository drill

`python -m scripts.operational_backup` supports only explicitly acknowledged development/test SQLite and filesystem fixtures. It refuses staging/production, existing restore targets, traversal manifests, and checksum mismatches. Example from `backend`:

```text
python -m scripts.operational_backup backup --database test.db --storage badges=badges --output .pytest_tmp/backup --acknowledge-test-data
python -m scripts.operational_backup verify --bundle .pytest_tmp/backup
python -m scripts.operational_backup restore --bundle .pytest_tmp/backup --database-target .pytest_tmp/restored.db --storage-target .pytest_tmp/restored-uploads --acknowledge-test-data
```

For PostgreSQL, use the selected provider's consistent snapshot or `pg_dump`/`pg_restore` with credentials supplied out of band. Restore into isolation, verify schema heads, database consistency, upload checksums/ownership, readiness, and representative role workflows before cutover. Never overwrite a live database as a rehearsal.
