# Platform Admin Production Implementation

Date: 2026-07-13

## Delivered

- Canonical guarded routes under `/admin` for overview, users/detail, organizations/detail, courses/detail, badges, and reports.
- Role-accurate navigation and canonical Admin login destination.
- Partial-failure Admin overview with supported user, role, organization-membership, course, badge, and analytics counts.
- Privacy-minimized responsive user directory; individual identity/role detail; confirmed role changes; self-role/self-delete prevention; confirmed permanent deletion.
- Explicitly scoped, read-only organization visibility using only current-account memberships.
- Course oversight and governance summary separated from Content Studio; no authoring controls; confirmed destructive deletion.
- Badge creation/upload for `admin`, read-only catalog for compatible `super_admin`, accessible image naming, and explicit unsupported lifecycle behavior.
- Defined platform report over `/api/analytics/overview`.
- Shared loading, empty, error, permission, success, and confirmation patterns across new pages.
- Seeded Admin Playwright smoke and guarded student deep-link scenario.

## Components Created

`AdminOverviewComponent`, `AdminUserDetailComponent`, `AdminOrganizationsComponent`, and `AdminReportsComponent`; shared Admin production layout styles in `frontend/src/styles/_admin-production.scss`.

## Components Migrated

`AdminUsersComponent`, `AdminCoursesComponent`, `AdminBadgesComponent`, role selector, route configuration, shell navigation, and permission navigation mapping.

## APIs Used

`GET /api/users`, `GET/PUT/DELETE /api/users/{id}`, `GET /api/orgs`, `GET /api/courses`, `GET /api/courses/{id}`, `GET /api/courses/{id}/governance-summary`, `DELETE /api/courses/{id}`, `GET/POST /api/badges`, `POST /api/upload/badge`, and `GET /api/analytics/overview`.

## Not Implemented

Moderation, platform settings, platform-wide organization directory/membership oversight, organization lifecycle actions, badge edit/delete/archive, account disable/restore, invitation actions, audit logs, asset library, and unsupported `super_admin` inheritance.

## Backend Repair

The existing user detail and update route parameters now use `uuid.UUID`, preventing UUID-column binding failures. The existing static `/api/users/students` route is registered before `/api/users/{user_id}` so it is no longer shadowed. No schema, migration, new endpoint, seed behavior, or JWT behavior changed.

## Verification

- Frontend unit tests: `245 SUCCESS` (baseline was 233).
- Backend unit tests: `224 passed`, including new UUID detail/update and static student-route regressions.
- Production build: passes; existing Sass mixed-declaration deprecation warnings remain.
- Playwright discovery: 3 tests in 2 files, including 2 Admin scenarios.
- Seeded browser execution: executed serially against a disposable, model-created SQLite database because Docker/PostgreSQL were unavailable. The Admin oversight, unauthorized Admin deep-link, and student flagship flows pass. Result: `3 passed`.
- OpenSpec: `openspec validate overhaul-role-based-ui-ux-experience --strict` passes.
