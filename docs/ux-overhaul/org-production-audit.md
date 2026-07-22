# Organization Administration Production Audit

Date: 2026-07-14

## Scope and role model

The Organization product area belongs to an authenticated user whose active organization membership role is `org_admin`. Platform role alone is not sufficient: canonical routes continue to use `RoleGuard`, and every organization API must validate the active membership and requested organization identifier. Organization administrators manage one active organization context at a time and do not receive platform-global Admin or Studio controls.

The existing `PermissionsService` combines the token role, active organization role, organization bootstrap, and navigation permissions. The canonical implementation must continue to use that service rather than introducing a second role resolver.

## Route and screen audit

| Current route or surface | User goal | Current roles | APIs | Sensitivity | Current capability | Backend authorization | Current risks | Migration recommendation | Product area |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `/workspace/learners` | Enter organization/learner operations | Broad creator roles | None directly | Medium | Generic role selector, not an organization dashboard | Frontend guard only for the page | Mixed role language and no organization summary | Canonical `/organization`; retain legacy route | Organization |
| `/workspace/settings/invites` | Invite organization members | `org_admin`, `content_admin` in frontend | `GET/POST /api/orgs/{org_id}/invites` | High: email, role, invite token | Create and list | `require_org_roles("org_admin")` plus requested-org match | Frontend exposes invite tokens; content-admin route guard is broader than backend; no loading/error state; unsupported parent role offered | Canonical `/organization/invitations` for `org_admin`; never render tokens; retain legacy route | Organization |
| `/workspace/learners/cohorts` | List and create classes | teacher/instructor/org-admin | `GET/POST /api/sections`, section summary | High: class and learner activity | List returns only sections created by or enrolling current user; create requires raw course-version UUID | Create uses active membership; list is current-user scoped, not organization scoped | Organization admin cannot see the organization; raw UUID input; partial summaries; misleading completeness | Canonical `/organization/sections` over an organization-scoped read contract; retain legacy teacher view | Organization/Teach |
| `/workspace/learners/cohorts/:id` | Inspect class roster and assignments | teacher/instructor/org-admin | roster, assignments, section summary, users/students, courses | Very high: learners and progress | Existing teacher-oriented detail | Roster and summary require an allowed active-org role but do not verify section organization; users/students rejects org-admin | Cross-organization ID probing can disclose enrollment/progress aggregates; calls occur before list membership is confirmed | New organization detail must resolve section through a scoped list before nested reads; backend scope fix required | Organization/Teach |
| `/home/sections` and `/:id` | Teacher class workflow | teacher/instructor/org-admin | Same section APIs | Very high | Teacher authoring/assignment experience | Mixed platform and org-role checks | Organization responsibilities are mixed with teacher assignment work | Keep as Teach/legacy; Organization uses separate oversight pages | Teach |
| `/workspace/access` | Manage product access grants | Broad creator roles | V2 products and access grants | High: learner IDs and access | Create/revoke with raw user UUID | Workspace visibility scope; creator-role checks | No organization member validation for grant target; raw IDs; no confirmation in legacy page | Canonical Organization course availability is read-only until member-safe grant targeting exists | Studio/Organization boundary |
| `/workspace/settings` | Personal preferences and organization name | Broad creator roles | preferences; `GET/PATCH /api/orgs` | Medium | Personal settings plus name update | Update permits active org-admin/content-admin or super-admin | Mixed personal and organization settings; errors only via toast | Canonical `/organization/settings` exposes active organization identity and name only; personal preferences remain separate | Organization/Shared |
| `/workspace/analytics` | Operational wrapper analytics | Broad creator roles | V2 analytics | High aggregate | Workspace/content-product metrics | Membership-derived workspace scope | Content-production metrics do not answer organization administration questions | Do not migrate into Organization reporting; compose only defined organization counts | Studio |
| `/workspace/products` | View V2 product wrappers | Broad creator roles | `GET /api/products` | Medium | Workspace-scoped content wrappers | Membership-derived workspace scope | Includes non-course products and editorial states | Canonical `/organization/courses` filters course/program wrappers and labels limitations | Organization/Studio boundary |
| Admin organization pages | Platform oversight | admin/super-admin | `/api/orgs` | High | Current-account membership visibility only | Platform route guard | Not an org self-service experience | Remain in Admin; do not reuse as Organization | Admin |

## Backend capability audit

### Organizations

- `GET /api/orgs` returns only organizations in which the current user has a membership. Fields are ID, name, type, country, timezone, created date, and the current user's organization role.
- `PATCH /api/orgs/{org_id}` supports only `name`. It verifies current-user membership with `org_admin` or `content_admin`, or platform `super_admin`.
- `POST /api/orgs/{org_id}/switch` verifies membership and refreshes the active organization token context.
- Branding, contacts, announcements, lifecycle state, archival, billing, licensing, and district hierarchy do not exist.

### Members, teachers, and students

- `OrganizationMembership` stores organization, user, organization role, status, and creation time.
- No organization-scoped membership read endpoint exists.
- `/api/users` is platform-admin-only and `/api/users/students` is admin/teacher-only; neither is safe or authorized for Organization.
- No member removal, role-change, disable, bulk import, or export endpoint exists.
- A minimal organization-scoped member read endpoint is required to make existing membership data visible without exposing platform-global users.

### Invitations

- Organization admins can list and create invites for the active organization.
- The model exposes email, role, expiration, accepted timestamp, inviter, and a secret acceptance token.
- The canonical UI must omit the token and derive only `Pending`, `Accepted`, or `Expired` presentation from existing fields and current time.
- Resend and cancel APIs do not exist. They must not be represented as available actions.

### Sections and classes

- Create supports name, course-version ID, mode, and optional dates.
- The generic list endpoint is current-user scoped, not active-organization scoped.
- Roster and section summary endpoints authorize the caller's active organization role but fail to assert that the requested section belongs to that organization.
- Assignment routes share the existing teacher workflow and are outside this phase unless an organization-safe oversight contract is used.
- A scoped organization section list and section ownership validation are required before canonical detail pages can safely expose roster or summary data.

### Course availability and access

- `/api/courses` rejects `org_admin`.
- V2 products and access grants are membership/workspace scoped and include course/program wrapper relationships, visibility, review state, and access state.
- Product wrappers can support a read-only organization availability view. They are not equivalent to the full course catalog.
- Existing access-grant creation accepts any platform user UUID and does not verify organization membership, so the canonical Organization UI must not expose grant creation.

### Reporting

- Platform analytics reject `org_admin`; teacher analytics do not model Organization scope.
- V2 workspace analytics are scoped but describe content wrappers and access, not organization membership.
- Organization reporting may only compose counts from scoped members, invitations, sections, section enrollments, and available product wrappers. No engagement score, growth rate, or organization ranking is supported.

## Accessibility and responsive audit

- Legacy invite inputs use placeholders without programmatic labels and expose invite tokens.
- Legacy invite and access pages lack complete loading, failure, confirmation, and focus-restoration states.
- Legacy section creation requires users to paste a UUID and uses a desktop-oriented hierarchy.
- Existing class detail tabs and cards are teacher-oriented and call partially unsupported services for org-admin.
- Canonical pages require labeled controls, semantic responsive records, announced result counts, text statuses, 44px targets, dialog focus management, wrapping identifiers, and no horizontal tables at 390px.

## Implementation decision

Build a separate canonical `/organization/**` frontend family for organization oversight. Add only the narrowly required organization-scoped read contracts for members and sections, plus section ownership validation on existing nested reads. Reuse current invitation creation/listing, organization name update, V2 product reads, and shared state/confirmation infrastructure. Do not add invitation resend/cancel, member mutation, branding, billing, licensing, bulk operations, or invented analytics.
