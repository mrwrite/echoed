# Teacher Production Implementation

Date: 2026-07-12

## Implemented

- Canonical Teach route family:
  - `/teach`
  - `/teach/classes`
  - `/teach/classes/:id`
  - `/teach/curriculum`
  - `/teach/courses/:courseId/preview`
  - `/teach/assignments`
  - `/teach/learners/:learnerId`
- Teacher/instructor navigation now points to Teach routes.
- Legacy `/home/sections`, `/home/sections/:id`, and `/workspace/learners/cohorts` routes remain available.
- Teacher home reframed around today, classes, learner progress, curriculum preview, and honest review/discussion limitations.
- Classes list adds loading, empty, error, search, responsive cards, and explicit course-version contract copy.
- Class detail adds overview, roster, assignments, progress, and discussion tabs over existing APIs.
- Assignment creation uses confirmation dialog and preserves values on failure.
- Curriculum browse and course preview use existing course APIs.
- Learner detail is scoped to class roster context.

## Backend Changes

None.

## APIs Used

- `/api/courses`
- `/api/courses/{id}`
- `/api/users/students`
- `/api/analytics/teacher-summary`
- `/api/analytics/educator-runtime-support`
- `/api/sections`
- `/api/sections/{id}/roster`
- `/api/sections/{id}/assignments`
- `/api/sections/{id}/analytics/summary`

## Known Limitations

- Instructor-compatible UI exists, but some analytics endpoints still require backend support for `instructor`.
- Per-learner assignment state, feedback history, manual review, and return-work workflows are not verified.
- Unit/lesson assignment target pickers need richer APIs before they can avoid raw IDs.
- Discussion moderation remains deferred until thread/post APIs are scoped and authorized.

## Verification

- App TypeScript compile: `npx tsc -p tsconfig.app.json --noEmit` passed.
- Production build: `npm run build` passed with existing Sass deprecation warnings in global typography.
- Frontend unit tests: `npx ng test --watch=false --browsers=ChromeHeadless` passed with `233 SUCCESS`.
- Playwright discovery: `npx playwright test --list` passed; 1 demo smoke test discovered.
- Strict OpenSpec validation: `openspec validate overhaul-role-based-ui-ux-experience --strict` passed.
- Browser execution remains blocked because local TCP checks failed for frontend `127.0.0.1:4200`, backend `127.0.0.1:8000`, and PostgreSQL `127.0.0.1:5432`.
