# Administrator Screen Specifications

## Admin Dashboard

- Current: `AdminViewComponent`.
- Goal: understand platform health and risks.
- API: `/api/analytics/overview`, `/api/users`, `/api/courses`, governance summary, usage stats service.
- Layout: alerts, metrics, governance issues, recent users/courses, quick links.
- Backend changes: none.

## User Management

- Route/component: `/home/admin/users`, `AdminUsersComponent`.
- Goal: find, edit, deactivate/delete users.
- API: `/api/users`, `/api/users/{id}`.
- Desktop: searchable table with filters.
- Mobile: data list.
- Confirmation: required for delete/role changes.
- Backend changes: optional deactivate vs delete if not supported.

## Role Management

- Current: roles are user role and org membership role.
- Goal: safely adjust platform/org role.
- API: `/api/users/{id}`, org membership/invite APIs.
- Backend changes: optional dedicated role audit endpoint.

## Organization Management

- Current: `/api/orgs`, invites, active org switch.
- Goal: manage organizations and memberships.
- UI: organization list, detail, members, invites, settings.
- Backend changes: optional admin org list/detail if super admin needs all orgs.

## Curriculum / Course Management

- Route/component: `/home/admin/courses`, `AdminCoursesComponent`.
- API: `/api/courses`, governance endpoints.
- Goal: manage course lifecycle and safety.
- Confirmation: delete/archive/publish actions require dialog.
- Backend changes: none for current management; archive preferable if supported later.

## Reporting

- Current: analytics routes.
- Goal: inspect student, classroom, product, and platform reports.
- API: `/api/analytics/*`.
- Layout: filters, summary cards, accessible charts, export if supported.
- Backend changes: optional exports.

## Moderation

- Current: review center and posts/threads APIs.
- Goal: handle flagged content/discussions.
- Backend changes: likely required if flag/moderation states are not implemented.

## Uploads / Assets

- Current: badge/coloring/storybook upload endpoints and backend file folders.
- Goal: manage media safely.
- API: `/api/upload/*`.
- Backend changes: optional asset library/list/delete endpoints.

## Platform Settings

- Current: preferences and org settings only.
- Goal: configure app-level settings where supported.
- Backend changes: required only for new configurable settings.

## Audit-Sensitive Confirmation Flows

- Applies to: delete user, delete course, revoke access, publish product, change role.
- Requirements: object name, impact, irreversible/undo copy, typed confirmation for high-risk operations, success/failure record.
