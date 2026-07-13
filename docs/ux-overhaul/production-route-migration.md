# Production Route Migration

Phase 1 preserves route compatibility and establishes canonical role destinations without deleting deep links. Phase 2 begins the student `/learn` migration while keeping legacy student deep links available. Phase 3 adds canonical teacher `/teach` routes while preserving `/home` and workspace cohort deep links. Phase 4 adds the guarded `/admin` family and retains legacy Admin deep links.

| Current route | Canonical route | Role | Redirect behavior | Guard behavior | Migration phase | Removal criteria | Deep-link risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `/home` | `/teach` for teacher/instructor; `/admin` for admin/super_admin-compatible | teacher, instructor, admin, super_admin-compatible | No redirect; legacy role dashboard remains | `HomeSessionGuard`; child guards unchanged | Phase 4 Admin canonical landing added | Remove role-dashboard reliance only after compatibility redirect and usage validation | High |
| `/teach` | `/teach` | teacher, instructor | No redirect; role landing now points here | `HomeSessionGuard`; child guards unchanged | Phase 3 | None planned | Low |
| `/teach/classes` | `/teach/classes` | teacher, instructor, org_admin | No redirect | `HomeSessionGuard` plus `RoleGuard` section roles | Phase 3 | None planned | Low |
| `/teach/classes/:id` | `/teach/classes/:id` | teacher, instructor, org_admin | No redirect | `HomeSessionGuard` plus `RoleGuard` section roles; frontend verifies route section is in authorized section list | Phase 3 | None planned | Low |
| `/teach/curriculum` | `/teach/curriculum` | teacher, instructor | No redirect | `HomeSessionGuard` plus `RoleGuard` teacher/instructor | Phase 3 | None planned | Low |
| `/teach/courses/:courseId/preview` | `/teach/courses/:courseId/preview` | teacher, instructor | No redirect | `HomeSessionGuard` plus `RoleGuard` teacher/instructor; preview uses course load only | Phase 3 | None planned | Low |
| `/teach/assignments` | `/teach/classes` class-first assignment entry | teacher, instructor, org_admin | No redirect; currently renders class list to choose assignment context | `HomeSessionGuard` plus `RoleGuard` section roles | Phase 3 | Replace only if global assignment API is added | Low |
| `/teach/learners/:learnerId` | `/teach/learners/:learnerId?sectionId=` | teacher, instructor, org_admin | No redirect | `HomeSessionGuard` plus `RoleGuard`; frontend requires section context and roster membership | Phase 3 | None planned | Low |
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
| `/home/admin/users` and `/workspace/learners/users` | `/admin/users` | admin | Legacy routes remain; canonical navigation uses `/admin/users` | `HomeSessionGuard` plus `RoleGuard` admin-only | Phase 4 | Add explicit redirects after bookmark/usage validation | Medium |
| No legacy detail | `/admin/users/:userId` | admin | New route | `HomeSessionGuard` plus `RoleGuard` admin-only; backend exact admin check | Phase 4 | None planned | Low |
| No platform directory route | `/admin/organizations` and `:organizationId` | admin, super_admin | New scoped read-only routes | `HomeSessionGuard` plus `RoleGuard`; API returns current-account memberships only | Phase 4 | Replace only after platform directory API is approved | Low |
| `/home/admin/courses` and `/workspace/products/manage` | `/admin/courses` | admin | Legacy routes remain; canonical navigation uses `/admin/courses` | `HomeSessionGuard` plus `RoleGuard` admin-only | Phase 4 | Add explicit redirects after bookmark/usage validation | Medium |
| No legacy oversight detail | `/admin/courses/:courseId` | admin | New route | `HomeSessionGuard` plus `RoleGuard` admin-only | Phase 4 | None planned | Low |
| `/home/admin/badges` and `/workspace/settings/badges` | `/admin/badges` | admin; super_admin read-only compatible | Legacy routes remain admin-only; canonical route permits supported read compatibility | `HomeSessionGuard` plus `RoleGuard`; writes remain backend admin-only | Phase 4 | Add explicit redirects after bookmark/usage validation | Medium |
| `/workspace/analytics` | `/admin/reports` for platform counts; workspace route remains Studio analytics | admin | No redirect because definitions differ | `HomeSessionGuard` plus `RoleGuard` admin-only | Phase 4 | None; keep reporting domains separate | Low |
| `/home/sections` | `/teach/classes` | teacher, instructor, org_admin | No redirect | Existing `RoleGuard` section roles | Phase 3 alias added | Remove only after teacher bookmarks and smoke tests move to `/teach/classes` | High |
| `/home/sections/:id` | `/teach/classes/:id` | teacher, instructor, org_admin | No redirect | Existing `RoleGuard` section roles | Phase 3 alias added | Remove only after class detail deep links have compatibility redirects | High |
| `/home/courses` | `/home/courses` | teacher, instructor, student transitional | No redirect | Existing child route, no added guard | Phase 1 | Course library split is implemented and tested | Medium |
| `/home/programs` | `/home/programs` | teacher, instructor, student transitional | No redirect | Existing child route, no added guard | Phase 1 | Learning path route aliases are implemented and tested | Medium |
| `/home/certifications` | `/learn/certificates` for student-origin actions | student transitional | No redirect | Existing child route, no added guard | Phase 2 partial | Existing links aliased and achievements page redesigned | Medium |
| `/home/lesson/:id` | `/learn/lesson/:id` for student-origin actions | student transitional, staff preview transitional | No redirect | Existing authenticated guard; governed segment restore unchanged | Phase 2 partial | Remove only after staff lesson preview route is explicit and student bookmarks have an alias | High |
| `/home/me/preferences` | `/home/me/preferences` | all authenticated roles | No redirect | Existing authenticated shell | Phase 1 | Dedicated settings route aliases are implemented | Medium |

## Canonical Login Destinations

- `student`: `/learn`
- `teacher`: `/teach`
- `instructor`: `/teach`
- `content_admin`: `/workspace`
- `org_admin`: `/workspace/learners`
- `admin`: `/admin`
- `super_admin`: `/admin` with partial compatibility state

## Route Compatibility Notes

- Browser bookmarks are preserved; no broad route deletion was performed.
- Unauthorized routes remain protected by existing route guards. Hidden navigation is not treated as authorization.
- `/workspace/commercial` remains the technical path in this phase, but visible navigation now uses `Community`.
- Phase 2 updates student-origin actions from the legacy student dashboard to navigate into `/learn/**` while preserving `/home/**` deep links.
- Phase 2 adds `/learn/courses/:courseId` as the canonical student course overview and keeps `/learn/products` as a transitional browse route.
- No dedicated unit route was added because existing APIs do not expose unit-level student progress or direct-link authorization.
- Phase 3 adds canonical Teach routes without deleting `/home/sections`, `/home/sections/:id`, or `/workspace/learners/cohorts` compatibility routes.
- Teacher course preview intentionally avoids `/api/start-course`; it uses `/api/courses/{id}` only.
- Phase 4 does not add moderation or platform-settings routes because no safely authorized capability exists.
- `super_admin` is not treated as inherited `admin`; unsupported child routes stay guarded and hidden.
