# Admin Super-Admin Compatibility

Date: 2026-07-13

`super_admin` is a partial role, not an inherited superset of `admin`.

| Surface | `admin` | `super_admin` | Evidence |
| --- | --- | --- | --- |
| Admin shell/overview | Full supported overview | Visible limitation state | Frontend role navigation; core overview API is admin-only. |
| Users | Read/write/delete | Rejected | `require_roles("admin")`. |
| Courses | Read/write/delete | Rejected | `require_roles("admin", "teacher", "student")` and explicit write list. |
| Badges | Read/create/assign/upload | Read only | Badge list requires auth; writes compare role to `admin`. |
| Organizations | Current memberships only | Current memberships only; PATCH bypass exists | List is membership-scoped for every role; PATCH explicitly bypasses for super admin. |
| Admin report | Available | Rejected | Overview analytics requires `admin`. |
| V2 analytics | Unscoped | Unscoped | V2 role list and visibility helper include both. This remains Studio reporting. |

Canonical `/admin` accepts both roles. Users, courses, and reports routes accept only `admin`; organizations and badge catalog accept both. Navigation mirrors these facts. No control is exposed solely because the role is named `super_admin`.
