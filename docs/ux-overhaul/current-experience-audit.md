# Current Experience Audit

Date: 2026-07-10

Scope: static repository audit of the Angular frontend, FastAPI backend routes, seeded demo data, shared styles, and automated tests. A native browser walkthrough of every role was not completed in this phase; the findings below are grounded in file evidence.

## Verified Stack

| Area | Evidence | Finding |
| --- | --- | --- |
| Frontend | `frontend/package.json`, `frontend/src/app/app.routes.ts` | Angular 20 standalone components with Angular Router. |
| Styling | `frontend/tailwind.config.js`, `frontend/src/styles.scss`, page SCSS files | Tailwind plus global SCSS and page-local SCSS. There are overlapping token systems. |
| Backend | `backend/app/main.py`, `backend/app/api/routes/*.py` | FastAPI route modules for auth, orgs, users, courses, lessons, progress, analytics, V2 platform, sections, assignments, posts, threads, uploads. |
| Auth | `backend/app/auth.py`, `backend/app/api/routes/auth.py`, `frontend/src/app/services/auth.service.ts` | JWT token login at `/api/auth/token`, registration at `/api/auth/register`, token payload drives frontend session. |
| Guards | `frontend/src/app/guards/home-session.guard.ts`, `frontend/src/app/guards/role.guard.ts` | Authenticated shell requires `PermissionsService.bootstrapSession()`. Role-gated routes use canonical permissions. |
| Tests | `frontend/src/app/**/*.spec.ts`, `backend/tests` | Karma/Jasmine and pytest coverage exists for auth/org state, sidebar/header accessibility, learner/teacher/admin states, API services, progress, uploads, permissions. |
| Storybook | `frontend/.storybook`, `frontend/src/app/components/*.stories.ts` | Storybook exists for several components but is not a complete product design lab. |

## Current Product Shape

EchoEd currently contains three overlapping experiences:

1. Public marketing and public product pages: `''`, `/products`, `/products/:slug`.
2. Legacy role dashboard shell under `/home`: student, teacher, admin, courses, programs, certifications, sections, preferences, org invites, studio courses.
3. V2 workspace shell under `/workspace`: projects, product studio, products, knowledge sources, artifacts, review center, access, learners, analytics, community, settings.
4. Learner portal under `/learn`: learner dashboard, products, paths, certificates, resources, lessons.

The overlap creates cognitive load because the same domain appears under multiple route families with different labels: courses/products, sections/cohorts, admin course management/product management, `/home/lesson/:id` and `/learn/lesson/:id`.

## Roles and Access

Implemented roles and role concepts are verified in `backend/app/enum.py`, `backend/app/deps.py`, `frontend/src/app/services/permissions.service.ts`, and `frontend/src/app/app.routes.ts`.

| Role | Current status | Evidence |
| --- | --- | --- |
| Student | Implemented | `require_roles("student")` on enroll/start/certification routes; `/learn`; student dashboard component. |
| Teacher | Implemented | `require_roles("admin", "teacher")` for course creation and assignments; section org role access. |
| Admin | Implemented | `/home/admin/users`, `/home/admin/courses`, `/home/admin/badges`; backend user CRUD requires admin. |
| Org admin | Implemented | `OrganizationRole.ORG_ADMIN`; org invites, sections, workspace, studio courses. |
| Content admin | Implemented | `OrganizationRole.CONTENT_ADMIN`; studio courses, review/content operations. |
| Instructor | Implemented/partial | `OrganizationRole.INSTRUCTOR`; section and workspace nav, but fewer dedicated screens. |
| Parent | Partial | registration exposes parent and organization type family; no dedicated parent dashboard route. |
| Viewer | Partial/backend only | enum value exists; no clear frontend route model. |
| Super admin | Partial/backend privileged | backend bypass in org checks and V2 creator role; frontend route constants omit super_admin in some places. |

## Strengths

- Auth/session behavior is more robust than the visible UI suggests. `PermissionsService` prevents raw token-only navigation and tests cover failure, onboarding, and active org state.
- The shell already has a skip link, focusable main landmark, labeled sidebar controls, loading states, and org switching state.
- Student, teacher, and admin dashboards contain real learning operations, not only static cards.
- Backend APIs include mature governance, publish-readiness, safe-publish, competency integrity, runtime intervention, and V2 review/access concepts.
- Seed data provides realistic demo accounts and course content: `EchoEd Demo School`, `Introduction to Africa`, student archetypes, content admin dogfooding workspace.

## Highest Severity UX Problems

1. Navigation architecture is product-internal rather than role-task oriented. `/home`, `/workspace`, and `/learn` expose overlapping concepts with different labels.
2. The application shell title and copy say "Workspace OS" and "Command center" even for learner-facing routes, creating role confusion.
3. Student routes are split between `/home` and `/learn`; the canonical learner destination is unclear after login.
4. Teacher and admin dashboards combine operational priorities, course governance, quick actions, and reporting in dense pages with weak hierarchy.
5. Destructive actions such as course/user deletion exist in dashboard components without a documented confirmation pattern.
6. Registration supports parent/instructor concepts but does not provide role-specific post-registration journeys.
7. Content/community language is still inconsistent from prior commercialization work; `/workspace/commercial` now labels "Community" but the route and component name remain commercial.
8. Global SCSS contains two visual systems and some mojibake comments, making brand consistency fragile.
9. Empty/loading/error states exist but are unevenly applied across all screens and do not yet define a shared decision model.
10. Mobile navigation collapses to a sidebar overlay pattern but lacks a dedicated bottom/tab model for learners and rapid teacher tasks.

## Accessibility Concerns

- Positive: focus styles are globally retained and tested in `frontend/src/app/components/accessibility-focus.spec.ts`.
- Positive: loading states use status semantics and error panels use alert semantics in component specs.
- Risk: icon-only collapsed sidebar relies on `aria-label`/`title`; needs tooltip and target-size standardization.
- Risk: page-local cards and tables may not all provide responsive data-list alternatives.
- Risk: role selector and dense governance tables need screen-reader order review.
- Risk: motion is extensive in `styles.scss`; reduced-motion support exists but should be centralized in tokens.

## Responsive Concerns

- The shell collapses sidebar below 1024px in `HomeComponent.syncShellViewport()`.
- Current layout depends heavily on desktop sidebar mental models.
- Several data-heavy screens should switch to responsive data lists and task-first summaries rather than horizontally dense tables.
- Lesson mode correctly hides sidebar/header, but recovery and exit controls need consistent mobile placement.

## Brand and Assets

- No explicit logo asset was found by repository search. Current mark is text-based "EE" in `echo-header` and `echo-sidebar`.
- Relevant visual assets include `frontend/src/assets/maps/africa-reference.svg`, `world-context.svg`, storybook/coloring media in `backend/storybook` and `backend/colorings`, and social screenshots under `docs/screenshots`.
- `/mnt/data/logo_concept.webp` was not evaluated in this Windows workspace. If supplied later, treat it as source input for token and mark refinement.

## Product Design Implication

The redesign should preserve backend behavior and routes initially, but introduce a role-aware IA that resolves overlaps:

- Learners start in Learn.
- Educators start in Teach.
- Admins start in Admin.
- Content/community operators start in Studio.

The first implementation should create a clearer shell and shared component system before restyling individual screens.
