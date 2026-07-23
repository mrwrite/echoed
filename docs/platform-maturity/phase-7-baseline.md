# Phase 7 Repository Baseline

Date: 2026-07-23

## Repository state

| Item | Baseline |
| --- | --- |
| Branch | `aqw-echoed-dev` |
| Commit | `21c07367d664fcfdd128a7ca19e2f7e2f97b4b42` |
| Commit subject | `feat: overhaul role-based UX and organization administration` |
| Working tree before Phase 7 creation | Clean |
| Phase 6 change | `overhaul-role-based-ui-ux-experience` |
| Phase 6 validation | Strict validation passed on 2026-07-23 |
| Phase 6 task status | 33/33 complete |
| Phase 6 archive status | **Not archived**; the completed change remains under `openspec/changes/` and no matching archive directory exists |

Phase 7 started from the clean committed state above. The Phase 6 task file is a read-only compatibility boundary for this change.

## Verified Phase 6 quality baseline

| Gate | Baseline |
| --- | --- |
| Backend pytest | 228 passing tests |
| Angular Karma | 284 passing tests |
| Playwright | 16 passing Chromium tests |
| Angular production build | Passed with one initial-bundle warning |
| OpenSpec | Strict validation passed |
| Whitespace | `git diff --check` passed |

## Frontend production baseline

The before build was generated with `npm run build -- --stats-json` using Angular CLI 20.3.26 on Node 20.19.4.

| Output | Raw size | Estimated transfer |
| --- | ---: | ---: |
| Main | 1,166,868 bytes | 184.55 kB |
| Initial shared chunk | 161,494 bytes | 47.37 kB |
| Global styles | 57,946 bytes | 10.30 kB |
| Polyfills | 34,585 bytes | 11.33 kB |
| **Initial total** | **1.42 MB** | **253.55 kB** |
| Existing lazy animation chunk | 64,184 bytes | 17.16 kB |

Production uses the Angular application builder with optimization and tree shaking enabled by the production configuration defaults, output hashing enabled, and production source maps disabled by default. Development explicitly disables optimization and enables source maps.

The configured budgets in `frontend/angular.json` are:

- Initial bundle: warning at 1.25 MB; error at 1.5 MB.
- Any component style: warning at 10 kB; error at 12 kB.

## Existing capability-gap sources

- `docs/ux-overhaul/backend-gap-register.md` is the primary Phase 6 gap inventory, but Phase 7 must verify every entry against current code.
- `docs/ux-overhaul/org-data-contract.md` records the minimized organization contracts.
- `docs/ux-overhaul/org-production-audit.md` and `org-production-implementation.md` record the Phase 6 organization scope.
- `docs/ux-overhaul/production-route-migration.md` is authoritative for route compatibility.
- Existing OpenSpec main specs and active changes contain additional implemented and proposed curriculum/governance behavior; an active proposal is not evidence that production behavior exists.

## Existing security and operational sources

- `SECURITY.md` is the repository security policy and reporting entry point.
- `ARCHITECTURE.md` describes application boundaries and primary services.
- `README.md`, `CONTRIBUTING.md`, and `docker-compose.yml` document local setup.
- Alembic configuration and `backend/alembic/versions/` define the migration mechanism.
- `backend/scripts/reseed_demo.py` and demo scripts define seed behavior.
- `docs/echoed-v2-release-candidate.md` is the closest existing release checklist.

At baseline there is no canonical production deployment, backup/restore, disaster-recovery, observability, or hosting-provider runbook. Those absences are audited rather than filled with invented infrastructure assumptions.
