# Student Production Audit

Date: 2026-07-11

Scope: Phase 2 student Learn experience for `overhaul-role-based-ui-ux-experience`. This audit verifies the current student-facing implementation before production changes.

## Student Routes

| Route | Component | Current role/access behavior | API dependencies | Notes |
| --- | --- | --- | --- | --- |
| `/learn` | `HomeComponent` > `UserDashboardComponent` > `LearnerPortalComponent` | Authenticated through `HomeSessionGuard`; canonical student landing from `ShellNavigationService`. | `/api/student-courses`, `/api/courses`, `/api/analytics/student-progress`, `/api/students/{id}/badges`, `/api/programs`, `/api/students/me/certifications`, `/api/learner-portal/products`, `/api/start-course`, `/api/enroll`. | Was product-wrapper oriented. Needs learner-first continuation, active learning, available learning, progress, and achievements. |
| `/learn/products` | `LearnerProductsComponent` | Authenticated through `HomeSessionGuard`; no additional role guard. | `/api/learner-portal/products`, `/api/start-course`, `/api/enroll`. | Course-backed V2 product list. Needs learner-facing labels and error/empty states. |
| `/learn/paths` | `ProgramsComponent` | Authenticated through `HomeSessionGuard`; no additional role guard. | `/api/programs`, `/api/programs/{id}/enroll`. | Existing learning path surface remains available. |
| `/learn/certificates` | `CertificationsComponent` | Authenticated through `HomeSessionGuard`; no additional role guard. | `/api/certifications`, `/api/students/me/certifications`, `/api/certifications/{id}/evaluate`. | Existing certifications surface remains available. |
| `/learn/resources` | `LearnerResourcesComponent` | Authenticated through `HomeSessionGuard`; no additional role guard. | None. | Empty resource state only. |
| `/learn/lesson/:id` | `LessonViewComponent` | Authenticated through `HomeSessionGuard`; uses governed segment restore. | `/api/progress/segment`, `/api/lessons/{id}`, `/api/progress/segment/complete`, `/api/student-courses`. | Reuses current lesson runtime and interrupted-session recovery. Needs canonical `/learn` exit behavior and save/completion state copy. |
| `/home` | `UserDashboardComponent` > `EchoedRoleSelectorComponent` > `StudentViewComponent` for student role | Authenticated through `HomeSessionGuard`; transitional route. | `/api/student-courses`, `/api/courses`, `/api/analytics/student-progress`, `/api/students/{id}/badges`, `/api/programs`, `/api/students/me/certifications`, `/api/start-course`, `/api/progress/segment/complete`. | Legacy student dashboard remains reachable. It has useful governed continuation behavior but routes to `/home/lesson/:id`. |
| `/home/courses` | `AvailableCoursesComponent` | Authenticated through `HomeSessionGuard`; shared staff/student route. | `/api/courses`, `/api/enroll`. | Legacy course catalog remains a compatibility route. |
| `/home/programs` | `ProgramsComponent` | Authenticated through `HomeSessionGuard`. | `/api/programs`, `/api/programs/{id}/enroll`. | Legacy learning paths route. |
| `/home/certifications` | `CertificationsComponent` | Authenticated through `HomeSessionGuard`. | `/api/certifications`, `/api/students/me/certifications`, `/api/certifications/{id}/evaluate`. | Legacy certifications route. |
| `/home/lesson/:id` | `LessonViewComponent` | Authenticated through `HomeSessionGuard`; governed segment restore. | `/api/progress/segment`, `/api/lessons/{id}`, `/api/progress/segment/complete`, `/api/student-courses`. | Legacy lesson deep links remain available. |

## Components and Current Behavior

- `frontend/src/app/pages/learner-portal/learner-portal.component.ts`
  - Current `/learn` home.
  - Uses `V2PlatformService.getLearnerProducts()`, `ProgramsService.getPrograms()`, `ProgramsService.getMyCertifications()`, `CoursesService.startCourse()`, and `CoursesService.enrollInCourse()`.
  - Existing copy exposes "products" as the primary learner concept and does not use `/api/student-courses` for continuation priority.

- `frontend/src/app/pages/learner-portal/learner-products.component.ts`
  - Lists enrolled and available V2 learner products.
  - Uses `CoursesService.startCourse()` and `CoursesService.enrollInCourse()` for course-backed items.
  - Current labels include product wrapper/governance wording that is clearer for staff than for K-5 learners.

- `frontend/src/app/pages/user-dashboard/student-view/student-view.component.*`
  - Legacy student dashboard under `/home`.
  - Uses student-course, analytics, badge, program, and certification APIs.
  - Implements continuation selection from current enrolled courses and runtime support guidance.
  - Still includes dashboard framing, demo timeline copy, and `/home` navigation targets.

- `frontend/src/app/pages/lesson-view.component.*`
  - Shared lesson runtime for `/home/lesson/:id`, `/workspace/lesson/:id`, and `/learn/lesson/:id`.
  - Restores governed segment with `CoursesService.getCurrentSegment()`.
  - On 404 stale segment, recovers through `CoursesService.getStudentCourses()` and navigates to the active `unit_progress_id`.
  - Marks completion only after `CoursesService.markSegmentCompleted()` succeeds.

- `frontend/src/app/shared/lesson-viewer.component.*`
  - Shared learner lesson rendering.
  - Hides educator-only notes in learner mode and emits `segmentCompleted` from the final learner action.
  - Existing tests cover learner prompt visibility, quiz labels, step sequence, and progress display.

- `frontend/src/app/pages/assessment-detail/assessment-detail.component.*`
  - Existing student assessment route under `/home/assessments/:id`.
  - Uses `ProgramsService.getAssessment()` and `ProgramsService.submitAssessment()`.
  - Preserves answers on submit failure and blocks unavailable learner delivery.

## Services and API Contracts

- `CoursesService.getStudentCourses()` -> `GET /api/student-courses`
  - Source for enrolled/current courses, continuation guidance, status, progress, and `unit_progress_id`.
- `CoursesService.getCourses()` -> `GET /api/courses`
  - Source for currently visible course catalog.
- `CoursesService.startCourse()` -> `POST /api/start-course`
  - Authoritative start/resume operation. UI must navigate only when `delivery_state === 'governed_available'` and `unit_progress_id` is present.
- `CoursesService.getCurrentSegment()` -> `GET /api/progress/segment?student_unit_id=...`
  - Authoritative lesson-session restore.
- `CoursesService.markSegmentCompleted()` -> `POST /api/progress/segment/complete`
  - Authoritative completion/advance operation.
- `CoursesService.getLessonById()` -> `GET /api/lessons/{id}`
  - Authoritative lesson payload.
- `AnalyticsService.getStudentProgress()` -> `GET /api/analytics/student-progress`
  - Learner progress metrics and badge progress.
- `BadgesService.getStudentBadges()` -> `GET /api/students/{id}/badges`
  - Earned badge display.
- `ProgramsService.getPrograms()` -> `GET /api/programs`
  - Structured learning paths.
- `ProgramsService.getMyCertifications()` -> `GET /api/students/me/certifications`
  - Earned certification display.
- `V2PlatformService.getLearnerProducts()` -> `GET /api/learner-portal/products`
  - Course/program access wrappers; useful for available learning but should not replace the course runtime model.

## Testing Baseline

- `frontend/src/app/pages/user-dashboard/student-view/student-view.component.spec.ts` covers continuation, loading/error/empty states, support guidance, badge/program/certification surfaces, and no staff publish-readiness UI.
- `frontend/src/app/pages/lesson-view.component.spec.ts` covers governed unavailable states, loading, stale segment recovery, demo lesson selection, and exit control label.
- `frontend/src/app/shared/lesson-viewer.component.spec.ts` covers learner-safe lesson content rendering and quiz controls.
- `frontend/tests/demo/student-flagship-smoke.spec.ts` signs in as a seeded student and opens the governed lesson path from `/learn`.

## UX Problems Verified

1. `/learn` used "products" as the dominant learner concept instead of active learning and next lesson.
2. Continuation on `/learn` did not prioritize `/api/student-courses`; it relied on V2 learner products first.
3. Legacy student flow under `/home` had stronger continuation/progress behavior but sent students to `/home/lesson/:id`.
4. Available learning copy exposed wrapper/runtime details rather than learner-centered course language.
5. The lesson runtime exit action returned to `/home`, even when entered from canonical `/learn`.
6. Completion dialog copy said "dashboard" rather than "Learn".
7. No `/learn` unit/course overview route currently exists beyond product and course cards; this phase can improve hierarchy in cards without changing backend contracts.
8. Student assignment surfaces are not exposed as a distinct API-backed `/learn` route; assigned learning is currently represented by enrolled/current courses.
9. Resource page is an empty placeholder; it must not imply unsupported downloadable resources are ready.
10. Legacy `/home` routes remain necessary during migration and should not be deleted in this phase.

## Backend Change Assessment

No backend changes are required for this phase. The existing APIs provide enough data for a learner-first `/learn` home, course cards, progress summary, certification/badge states, and governed lesson recovery. A dedicated student assignment endpoint could improve future IA but is not required to preserve current behavior.
