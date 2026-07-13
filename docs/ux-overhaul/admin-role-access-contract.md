# Admin Role And Access Contract

Date: 2026-07-13

## Role Sources

Platform role is `User.role`; organization role is `OrganizationMembership.role`. They are additive in the frontend session but are checked independently by backend dependencies. There is no role inheritance.

| Role | Product status | Platform scope | Assignable in Admin user detail | Backend notes |
| --- | --- | --- | --- | --- |
| `student` | Implemented | Learner | Yes | Exact role checks protect learner APIs. |
| `teacher` | Implemented | Educator | Yes | Course CRUD and educator APIs recognize it. |
| `admin` | Implemented | Platform | Yes, with confirmation | Only role accepted by core Admin user, summary, and badge-write APIs. |
| `org_admin` | Implemented | Organization membership | No | Must be managed as organization membership; not through platform role control. |
| `content_admin` | Implemented | Organization/content membership | No | Studio/content access; not a platform Admin role. |
| `instructor` | Partial | Educator compatibility | No | Several educator endpoints still omit it. |
| `parent` | Partial | Unsupported portal | No | No complete navigation/API experience. |
| `viewer` | Partial | Unsupported portal | No | No complete navigation/API experience. |
| `super_admin` | Partial | Organization update bypass and V2 analytics | No | Does not inherit `admin`; core Admin APIs reject it. |

## Role Change Contract

- Admin can change another account among `student`, `teacher`, and `admin` through `PUT /api/users/{id}`.
- The complete safe identity DTO is resubmitted because the endpoint is not role-specific; password is sent as empty so the backend leaves it unchanged.
- Confirmation names the user and explains platform-area impact. UI state changes only after success.
- Self-role changes are disabled. The backend has no final-admin or self-lockout protection, so the UI also documents this unresolved enforcement gap.
- Organization roles and partial roles are not offered. Navigation is re-evaluated on next authenticated session; authenticated self-change is not exposed.

## Known Authorization Gaps

The backend accepts arbitrary `role` strings in `UserDto`, serializes ORM user objects without a dedicated privacy response schema, and does not protect the last administrator. Frontend constraints reduce accidental misuse but are not security boundaries.
