# Organization Administrator Role Capability Map

Date: 2026-07-14

## Effective role

The Organization area is available only when the authenticated session has an active organization membership with role `org_admin`. The frontend `RoleGuard` uses the existing `PermissionsService`; API dependencies remain authoritative. A platform `admin`, `content_admin`, teacher, or student does not gain Organization access from the platform role name alone.

## Supported capabilities

| Capability | Access | Scope | API authority |
| --- | --- | --- | --- |
| View organization overview | Read | Active organization | Scoped member, invite, section, and product reads |
| View members, teachers, and students | Read | Active organization | `GET /api/orgs/{org_id}/members` |
| View invitations | Read | Active organization | `GET /api/orgs/{org_id}/invites` |
| Create invitation | Write | Active organization | `POST /api/orgs/{org_id}/invites` |
| View classes and class detail | Read | Active organization | Scoped organization sections, roster, and summary APIs |
| View available learning offerings | Read | Active organization workspace | V2 products and access-grant reads |
| Rename organization | Write | Active organization | `PATCH /api/orgs/{org_id}` |

## Unsupported or read-only capabilities

- Member removal, role changes, activation changes, and bulk roster operations have no verified API.
- Invitation resend and cancellation have no API.
- Canonical class pages are oversight-only; teacher assignment and class-authoring workflows remain in Teach.
- Course availability is read-only because access-grant creation does not validate that its target belongs to the active organization.
- Branding, time zone editing, contact details, announcements, licensing, and district settings have no write contract.
- Platform users, global organizations, Studio authoring, learner grading, and platform reports are outside this role.

Organization membership and requested-object organization checks are enforced by the backend. Hidden navigation is never treated as authorization.
