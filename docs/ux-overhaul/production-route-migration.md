# Production Route Migration

Phase 1 preserves route compatibility and establishes canonical role destinations without deleting deep links.

| Current route | Canonical route | Role | Redirect behavior | Guard behavior | Migration phase | Removal criteria | Deep-link risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `/home` | `/home` for teacher/admin, transitional for other roles | teacher, instructor, admin, super_admin-compatible | No redirect | `HomeSessionGuard`; child guards unchanged | Phase 1 | Only after all role dashboards have route-level replacements and analytics show low usage | High |
| `/learn` | `/learn` | student | Login routes students here after ready bootstrap | `HomeSessionGuard`; learner child routes unchanged | Phase 1 | None planned | Low |
| `/workspace` | `/workspace` | content_admin | No redirect | `HomeSessionGuard` plus existing role guards | Phase 1 | None planned | Medium |
| `/workspace/learners` | `/workspace/learners` | org_admin | No redirect | Existing creator-role guard | Phase 1 | Replace only if organization home becomes a dedicated route | Medium |
| `/workspace/commercial` | `/workspace/commercial` with visible label `Community` | admin/content_admin/org_admin/teacher/instructor via existing creator role set | No redirect | Existing creator-role guard | Phase 1 | Add alias and deprecation only after community surface is redesigned | Medium |
| `/home/admin/users` | `/home/admin/users` | admin | No redirect | Existing `RoleGuard` admin-only | Phase 1 | Dedicated Admin IA route exists and old path is aliased | High |
| `/home/admin/courses` | `/home/admin/courses` | admin | No redirect | Existing `RoleGuard` admin-only | Phase 1 | Dedicated Admin IA route exists and old path is aliased | High |
| `/home/admin/badges` | `/home/admin/badges` | admin | No redirect | Existing `RoleGuard` admin-only | Phase 1 | Dedicated Admin IA route exists and old path is aliased | High |
| `/home/sections` | `/home/sections` | teacher, instructor, org_admin | No redirect | Existing `RoleGuard` section roles | Phase 1 | Class/cohort IA aliases are implemented and smoke tested | High |
| `/home/courses` | `/home/courses` | teacher, instructor, student transitional | No redirect | Existing child route, no added guard | Phase 1 | Course library split is implemented and tested | Medium |
| `/home/programs` | `/home/programs` | teacher, instructor, student transitional | No redirect | Existing child route, no added guard | Phase 1 | Learning path route aliases are implemented and tested | Medium |
| `/home/me/preferences` | `/home/me/preferences` | all authenticated roles | No redirect | Existing authenticated shell | Phase 1 | Dedicated settings route aliases are implemented | Medium |

## Canonical Login Destinations

- `student`: `/learn`
- `teacher`: `/home`
- `instructor`: `/home`
- `content_admin`: `/workspace`
- `org_admin`: `/workspace/learners`
- `admin`: `/home`
- `super_admin`: `/home`

## Route Compatibility Notes

- Browser bookmarks are preserved; no broad route deletion was performed.
- Unauthorized routes remain protected by existing route guards. Hidden navigation is not treated as authorization.
- `/workspace/commercial` remains the technical path in this phase, but visible navigation now uses `Community`.
