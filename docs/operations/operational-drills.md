# Operational Drills

Run from `backend` in a development/test environment:

```text
python -m scripts.run_operational_drills
```

The runner refuses staging/production and uses a temporary directory. Each result includes duration, observed behavior, and pass/fail. It covers unsafe production configuration rejection; migration graph/startup/explicit-gate verification; ASGI startup, liveness, database-unavailable readiness, and shutdown; failed post-deploy verification; backup/integrity/restore/rollback/storage recovery; and synthetic secret rotation. Targeted tests additionally cover trusted/untrusted proxy behavior, host rejection, readiness success, corrupted backup rejection, and engine disposal.

Pass criteria: every supported result is true, no protected value is emitted, unavailable dependencies fail the correct gate, restored data/assets match, and temporary data is removed. A provider-specific production-equivalent rehearsal must additionally execute migrations against isolated PostgreSQL, terminate a real container/process with the platform signal, restore representative encrypted off-host backups, test traffic removal, and exercise external alert delivery. Those drills must never target uncontrolled production data.

Observed results and limitations are recorded in [Phase 11 verification](phase-11-operational-readiness-verification.md).
