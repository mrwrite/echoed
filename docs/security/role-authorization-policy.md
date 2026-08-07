# Canonical Role Authorization Policy

Backend constants in `app.security` are canonical. Unknown roles are denied; route declarations are validated against explicit allowlists. `admin` and `super_admin` are distinct platform roles. `teacher` and `instructor` are compatible teaching roles, not aliases for administration. Organization authority requires an active membership and is separate from a global role.

| Role | Platform scope | Organization scope | User management | Content / teaching / learner | Forum | Prohibited actions |
| --- | --- | --- | --- | --- | --- | --- |
| `student` | own session | student membership | none | own enrollment/progress | create; own edit/delete | admin/content/other learner records |
| `parent` | onboarding/session only | parent membership | none | no implied teaching | create; own edit/delete | administrative grants |
| `teacher` / `instructor` | no platform admin | active teaching membership | student summaries only | authorized sections/learners; owned legacy or scoped content | create; own edit/delete | cross-org content/users, platform roles |
| `content_admin` | no platform admin | active content membership | none | organization course authoring; no learner/user administration | create; own edit/delete | platform user management |
| `org_admin` | no platform admin | active organization administration | organization members/invites only | org sections/content; no global users | create; own edit/delete | grant platform roles/cross-org access |
| `admin` | platform administrator | only deliberate org paths | non-admin targets; cannot grant/target platform admins | broad compatible content/admin access | moderator | self role/delete, target admin/super admin |
| `super_admin` | highest platform scope | deliberate explicit bypass | all targets except self, subject to final-super invariant | broad deliberate access | moderator | self role/delete, remove final super admin |
| `viewer` (org only) | none | read permissions only where implemented | none | no mutation implication | normal authenticated author only | administrative/content mutation |

Reusable boundaries are `require_roles`, `require_org_roles`, `require_scoped_section`, content-to-course authoring checks, forum owner/moderator checks, and progress-to-student-course checks. Known authenticated denials use 403; cross-organization/object concealment uses 404. A platform role never substitutes for an organization role unless a route deliberately includes the super-admin path.
