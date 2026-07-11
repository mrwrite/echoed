# Production Route Migration

Phase 1 preserves route compatibility and establishes canonical role destinations without deleting deep links. Phase 2 begins the student `/learn` migration while keeping legacy student deep links available.

| Current route | Canonical route | Role | Redirect behavior | Guard behavior | Migration phase | Removal criteria | Deep-link risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `/home` | `/home` for teacher/admin, transitional for other roles | teacher, instructor, admin, super_admin-compatible | No redirect | `HomeSessionGuard`; child guards unchanged | Phase 1 | Only after all role dashboards have route-level replacements and analytics show low usage | High |
| `/learn` | `/learn` | student | Login routes students here after ready bootstrap | `HomeSessionGuard`; learner child routes unchanged | Phase 1 | None planned | Low |
| `/learn/products` | `/learn/products` visible as Courses, with course path links to `/learn/courses/:courseId` | student | No redirect | `HomeSessionGuard`; existing learner-product API still used | Phase 2 | Keep as transitional browse route until learner-product and course catalog surfaces are unified | Low |
| `/learn/courses/:courseId` | `/learn/courses/:courseId` | student | New canonical course overview; no redirect | `HomeSessionGuard`; course access remains enforced by backend endpoints and governed start behavior | Phase 2 | None planned; direct route should remain | Low |
| `/learn/paths` | `/learn/paths` | student | No redirect | `HomeSessionGuard`; existing programs API | Phase 2 partial | None until learning paths are redesigned | Low |
| `/learn/certificates` | `/learn/certificates` visible as Achievements | student | No redirect | `HomeSessionGuard`; existing certification APIs | Phase 2 partial | None until achievements are redesigned | Low |
| `/learn/resources` | `/learn/resources` | student | No redirect | `HomeSessionGuard`; no API | Phase 2 partial | Remove only if a supported resources surface is not planned | Low |
| `/learn/lesson/:id` | `/learn/lesson/:id` | student | No redirect; `:id` remains a student unit progress id | `HomeSessionGuard`; governed segment restore unchanged | Phase 2 | None planned | Low |
| `/workspace` | `/workspace` | content_admin | No redirect | `HomeSessionGuard` plus existing role guards | Phase 1 | None planned | Medium |
| `/workspace/learners` | `/workspace/learners` | org_admin | No redirect | Existing creator-role guard | Phase 1 | Replace only if organization home becomes a dedicated route | Medium |
| `/workspace/commercial` | `/workspace/commercial` with visible label `Community` | admin/content_admin/org_admin/teacher/instructor via existing creator role set | No redirect | Existing creator-role guard | Phase 1 | Add alias and deprecation only after community surface is redesigned | Medium |
| `/home/admin/users` | `/home/admin/users` | admin | No redirect | Existing `RoleGuard` admin-only | Phase 1 | Dedicated Admin IA route exists and old path is aliased | High |
| `/home/admin/courses` | `/home/admin/courses` | admin | No redirect | Existing `RoleGuard` admin-only | Phase 1 | Dedicated Admin IA route exists and old path is aliased | High |
| `/home/admin/badges` | `/home/admin/badges` | admin | No redirect | Existing `RoleGuard` admin-only | Phase 1 | Dedicated Admin IA route exists and old path is aliased | High |
| `/home/sections` | `/home/sections` | teacher, instructor, org_admin | No redirect | Existing `RoleGuard` section roles | Phase 1 | Class/cohort IA aliases are implemented and smoke tested | High |
| `/home/courses` | `/home/courses` | teacher, instructor, student transitional | No redirect | Existing child route, no added guard | Phase 1 | Course library split is implemented and tested | Medium |
| `/home/programs` | `/home/programs` | teacher, instructor, student transitional | No redirect | Existing child route, no added guard | Phase 1 | Learning path route aliases are implemented and tested | Medium |
| `/home/certifications` | `/learn/certificates` for student-origin actions | student transitional | No redirect | Existing child route, no added guard | Phase 2 partial | Existing links aliased and achievements page redesigned | Medium |
| `/home/lesson/:id` | `/learn/lesson/:id` for student-origin actions | student transitional, staff preview transitional | No redirect | Existing authenticated guard; governed segment restore unchanged | Phase 2 partial | Remove only after staff lesson preview route is explicit and student bookmarks have an alias | High |
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
- Phase 2 updates student-origin actions from the legacy student dashboard to navigate into `/learn/**` while preserving `/home/**` deep links.
- Phase 2 adds `/learn/courses/:courseId` as the canonical student course overview and keeps `/learn/products` as a transitional browse route.
- No dedicated unit route was added because existing APIs do not expose unit-level student progress or direct-link authorization.
