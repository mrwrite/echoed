# Teacher Production Audit

Date: 2026-07-12

## Summary

The audited teacher/instructor production surface uses the existing FastAPI auth, organization-role, section, assignment, course, learner-progress, assessment, and discussion APIs. No backend files or database schema changes were required for this phase.

## Routes Audited

| Route | User goal | Role access | API dependencies | Current UX problems found | Privacy/accessibility/responsive risks | Migration recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| `/home` | Teacher landing through role selector | `teacher`; now `instructor` compatible in role selector | `/api/courses`, `/api/users/students`, `/api/analytics/teacher-summary`, governance summary | Old dashboard mixed demo/governance/course-authoring language with teacher work | Progress rows are not class-scoped; dense legacy tables; demo copy | Canonical `/teach`; keep `/home` legacy |
| `/teach` | Teacher Teach overview | `teacher`, `instructor` through shell/bootstrap | Same as `/home` teacher view | New canonical route added | Must not imply unsupported review/feedback counts | Canonical Phase 3 route |
| `/home/sections` | List/create sections | `teacher`, `instructor`, `org_admin` | `/api/sections`, `/api/sections/{id}/analytics/summary` | Thin CRUD, exposed internal course version ID without explanation | No loading/error states; no responsive data-list | Keep as legacy alias; canonical `/teach/classes` |
| `/teach/classes` | List/create classes | `teacher`, `instructor`, `org_admin` | Same as `/home/sections` | New production class list | Course version ID is still technical due to backend contract | Canonical Phase 3 route |
| `/home/sections/:id` | Manage section assignments | `teacher`, `instructor`, `org_admin` | `/api/sections`, `/api/sections/{id}/roster`, `/api/sections/{id}/assignments`, `/api/sections/{id}/analytics/summary`, `/api/users/students`, `/api/courses` | Old page only created assignment by raw target ID | Roster endpoint returns no learner profile fields; section ownership check is incomplete in backend | Keep as legacy alias; canonical `/teach/classes/:id` |
| `/teach/classes/:id` | Class overview, roster, assignments, progress, discussion note | `teacher`, `instructor`, `org_admin` | Same as section detail | New production class detail | Frontend verifies selected section is in authorized section list; backend remains authoritative | Canonical Phase 3 route |
| `/teach/curriculum` | Browse curriculum for assignment | `teacher`, `instructor` | `/api/courses` | New route | Client-side search only; no standards/duration invented | Canonical Phase 3 route |
| `/teach/courses/:courseId/preview` | Preview learner course hierarchy | `teacher`, `instructor` | `/api/courses/{id}` | New route | Does not call `/api/start-course`; no progress is recorded | Canonical Phase 3 route |
| `/teach/assignments` | Assignment entry point | `teacher`, `instructor`, `org_admin` | `/api/sections`, section assignment APIs after class selection | New alias to class list | Global assignment list endpoint does not exist | Keep as class-first assignment entry |
| `/teach/learners/:learnerId?sectionId=` | Learner detail with class context | `teacher`, `instructor`, `org_admin` | `/api/sections`, `/api/sections/{id}/roster`, `/api/users/students` | New route | Requires section context and roster membership; no global learner profile exposure | Canonical Phase 3 scoped learner detail |
| `/workspace/learners/cohorts` | Legacy class alias under workspace | creator roles; cohort child uses section roles | `/api/sections` | Commercial/workspace mental model for teachers | Route name does not match teacher task | Preserve legacy alias, do not promote |
| `/home/courses` | Legacy mixed course catalog | unguarded child under authenticated home | student/teacher transitional | Student and teacher goals mixed | Possible wrong mental model | Teacher navigation now uses `/teach/curriculum` |
| `/home/assessments/:id` | Assessment detail/submission | authenticated child; submit requires student | `/api/assessments/{id}`, `/api/assessments/{id}/attempts` | Student-oriented submit flow | Teachers can view assessment questions but no review/feedback workflow | Use as assessment preview only; no teacher grading |
| `/workspace/review-center` | Content review center | creator roles | V2 review center APIs | Content/studio review, not student work review | Could confuse teacher feedback | Not exposed in Teach nav |
| `/threads`, `/posts` APIs | Discussion primitives | No route guards in audited backend modules | `/api/threads`, `/api/posts` | No class scope or moderation permission model | High privacy risk if exposed as teacher moderation | Document gap; do not expose class feed |

## Backend Authorization Risks Found

- `GET /api/sections/{id}/roster` requires a teacher/org/instructor org role, but does not verify the section belongs to that organization.
- `POST /api/sections/{id}/enrollments` has the same section-scope risk.
- `GET /api/sections/{id}/assignments` currently has no explicit role dependency.
- `GET /api/analytics/teacher-summary` supports `admin` and `teacher`, but not `instructor`.
- Thread/post endpoints are not authenticated or class-scoped in the audited files.

Frontend work keeps navigation and views scoped, but these backend risks remain documented gaps.
