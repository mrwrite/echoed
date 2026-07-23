# Organization Administration Data Contract

Date: 2026-07-14

## Organization

`GET /api/orgs` supplies the organizations available to the current account. The canonical experience uses the active organization ID from the authenticated organization context. Visible fields are name, type, country, time zone, creation date, and the current account's organization role. Only `name` is writable through `PATCH /api/orgs/{org_id}`.

## Members

`GET /api/orgs/{org_id}/members` is an organization-admin-only, requested-organization-scoped read. It returns membership ID, user ID for routing/internal correlation, display name, username, organization role, membership status, and join date. It intentionally omits email, password hashes, authentication details, tokens, profile data, and memberships in other organizations.

Teacher views filter organization roles `teacher` and `instructor`; student views filter `student`. Counts and filters operate on this scoped response.

## Invitations

Existing invite reads provide email, requested role, expiration, acceptance timestamp, and creation context. The UI derives only `Pending`, `Accepted`, or `Expired`. Acceptance tokens are never rendered. Existing writes create an invite; the UI does not imply resend or cancellation support.

## Classes

`GET /api/orgs/{org_id}/sections` returns every class in the active organization with name, course-version reference, mode, dates, creator, and aggregate learner/teacher counts. Class detail uses the existing roster and section summary only after backend ownership validation. Roster presentation is minimized to organization member identity, role, status, and enrollment role.

## Learning availability

V2 product reads provide workspace-scoped course, learning-path, and certification wrappers. Access-grant reads support aggregate availability counts. The Organization UI does not expose Studio fields or mutation controls and does not claim this is a complete global course catalog.

## Reporting definitions

- Members, teachers, and students: active-organization membership records matching the displayed filters.
- Pending invitations: unaccepted invites whose expiration is in the future.
- Active classes: organization classes whose available date range includes the current time, or whose missing bounds do not exclude the current time.
- Available learning offerings: scoped course, learning-path, and certification product wrappers returned by current APIs.

These are operational counts, not engagement, performance, growth, or comparative analytics.
