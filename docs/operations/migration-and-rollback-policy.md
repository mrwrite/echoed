# Migration and Rollback Policy

Migrations execute once, before application rollout, through `backend/migrate.sh`; normal startup never changes schema. Failure, timeout, or head mismatch stops rollout. PostgreSQL backup completion is mandatory before a risky migration. Verify migration heads, readiness, and a safe read/write smoke afterward.

Migration authors must state whether the change is expand/contract compatible, locking/volume risk, and reversibility. Alembic `downgrade` presence is not proof of safe reversal. Data loss, column/type contraction, and backfills require a tested restore or forward-repair plan.

Rollback decision:

- Application rollback: redeploy the prior immutable SHA/digest only when it is compatible with the current schema and configuration.
- Configuration rollback: restore the prior reviewed non-secret configuration and appropriate credential version, revalidate, redeploy, and verify health. Never paste old secrets into evidence.
- Database rollback: use an explicitly tested downgrade only if declared safe; otherwise restore the pre-migration database and matching uploads to an isolated target, verify, then perform a controlled cutover.

Application-only rollback is unsafe after a backward-incompatible schema change. If compatibility is unknown, contain traffic and escalate rather than guessing. Database restore can discard post-backup writes and therefore requires an approved recovery point and stakeholder decision.
