# Phase 12 Platform Audit Events Verification

Recorded 2026-08-13 for `implement-platform-audit-events`.

## Starting state

- Branch/commit: `aqw-echoed-dev` at `e67300b3c5a0d2f720eca8fa1c968eb02a610308`.
- The worktree was clean before the Phase 11 spec sync/archive; those archive changes were preserved as the intentional starting delta for Phase 12.
- `establish-operational-readiness` was complete and strictly valid, was synced to `openspec/specs/platform-operational-readiness/spec.md`, and is archived at `openspec/changes/archive/2026-08-13-establish-operational-readiness`.
- Previous verified baselines were 299 backend, 308 Angular, and 23 Playwright tests.

## Implemented contract

- Added Alembic revision `b8f4c2d6e1a0` and the explicit `audit_events` model. Events retain actor/role and target identifiers without destructive foreign-key cascades.
- Added a centralized action catalog, primitive state allowlists, sensitive-key rejection, canonical SHA-256 hashing, per-scope sequence uniqueness, PostgreSQL transaction advisory locking, ORM update/delete rejection, and chain verification.
- Audit appends flush but never independently commit, so covered events share the business transaction and roll back with it.
- Covered supported role change, account deletion, organization invitation/acceptance membership, forum moderator deletion, course review/publish, artifact/product review, product publish, export, and retention operations. Unsupported restore/moderation workflows are not fabricated.
- Added platform and active-organization-admin scoped read APIs, concealment for cross-organization requests, bounded cursor pagination, allowlisted filters, explicit minimized schemas, capped formula-safe CSV, and export rate limiting.
- Added privacy-safe capture/read/export/verification/retention metrics and diagnostics without identifier labels or state payloads.
- Added the guarded `scripts/manage_audit_events.py` verification/retention command. Retention defaults to dry-run; production application requires acknowledgement, a safe backup reference, and no preservation hold.
- Added the guarded Angular Platform Admin route, navigation, list/detail/filter/pagination/export states, accessible error status, and stale protected-data clearing.
- Updated SQLite backup acceptance to verify every restored platform/organization chain when the audit table exists.

## Verification evidence

| Verification | Result |
| --- | --- |
| Focused audit and operational tests | 30 passed before the sequence/immutability hardening |
| Final focused audit tests | 14 passed |
| Complete backend suite | 313 passed, 4,225 warnings, 132.14 seconds; baseline increased by 14 |
| Python compile check | `python -m compileall -q app scripts` passed |
| PostgreSQL migration drill | Fresh PostgreSQL 15 database upgraded through the entire history to `b8f4c2d6e1a0 (head)` |
| SQLite new-revision compatibility | Prior head stamped and upgraded to `b8f4c2d6e1a0`; full legacy SQLite history remains unsupported by an older pre-existing `ALTER COLUMN` migration |
| Backup/restore drill | Test SQLite backup, manifest verification, isolated restore, row usability, and restored audit-chain verification passed in backend tests |
| Angular application typecheck | `tsc --noEmit -p tsconfig.app.json` passed |
| Angular spec typecheck | `tsc --noEmit -p tsconfig.spec.json` passed; five new audit specs compile |
| Angular browser tests | Not completed locally: Angular bundle setup exhausted the Windows process memory limit before assertions; an isolated Docker retry ended with Docker transport exit 255 during `npm ci` |
| Production Angular build | Not completed locally: build exhausted the same constrained Node process heap; application typecheck passed |
| Playwright collection | 23 tests in 9 files compile and enumerate, including authorized audit review and denied direct-route assertions |
| Playwright execution | Not rerun because the full seeded frontend/backend demo stack was not active; prior verified baseline remains 23 |
| Production dependency audit | `npm audit --omit=dev`: 0 vulnerabilities |
| Strict OpenSpec | `openspec validate implement-platform-audit-events --strict`: valid |
| Diff whitespace | `git diff --check`: passed before this evidence update and rerun at final handoff |

The temporary PostgreSQL container and local migration/test databases were removed after verification. No dependency was added or removed. The single additive database migration is intentionally retained on application rollback so accumulated audit history is not destroyed.

## Privacy, integrity, and access evidence

Tests prove sensitive or nested state fails closed; explicit responses omit hashes and internal scope keys; CSV neutralizes formula prefixes; learner reads fail; organization administrators see only an active matching organization; and denied/rolled-back mutations do not create successful records. Direct application ORM updates/deletes fail. A low-level modification causes chain verification to fail.

The integrity chain is not externally anchored. A fully privileged database operator can rewrite rows and hashes, and deliberate guarded retention can remove an old prefix that cannot subsequently be proven without an independent anchor. Production database permissions, encrypted backup storage, legal retention decisions, and external/WORM anchoring remain operator/infrastructure responsibilities.

## Remaining gate

Implementation, backend verification, migration/restore drills, documentation, strict validation, and static frontend checks are complete. The phase remains partially complete until the unchanged CI-class Angular browser suite, production build, and seeded Playwright execution pass in a runner with adequate memory and the demo stack. No result is represented as passed when its runner did not execute.

Recommended follow-up after those verification gates pass: archive `implement-platform-audit-events`, then reassess the roadmap for `implement-curriculum-authoring` versus a narrowly scoped beta-release readiness change. External audit anchoring should remain an infrastructure/security follow-up, not be folded into product authoring.
