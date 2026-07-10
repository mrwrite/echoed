# Role Capability Matrix

Evidence: `backend/app/enum.py`, `backend/app/deps.py`, `backend/app/api/routes/*.py`, `frontend/src/app/services/permissions.service.ts`, `frontend/src/app/app.routes.ts`, `backend/app/seed_demo.py`.

## Role Status

| Role | Status | Current entry points | Primary capabilities | Gaps |
| --- | --- | --- | --- | --- |
| Student | Implemented | `/home`, `/learn` | Enroll, start course, continue governed lessons, submit assessments, view programs/certifications/badges/progress. | Two learner route families; no child-specific navigation model. |
| Teacher | Implemented | `/home`, `/workspace`, `/home/sections` | View courses/students, assign courses, manage sections, inspect classroom progress and runtime support. | Dashboard mixes course authoring, governance, reporting, and class management. |
| Admin | Implemented | `/home/admin/*`, `/workspace` | Manage users/courses/badges; view admin overview and governance states. | Needs confirmation flows and audit-sensitive UX. |
| Org admin | Implemented | `/workspace`, org invites, sections, studio courses | Manage org invites, sections, studio course authoring, workspace access. | No dedicated organization administration hub. |
| Content admin | Implemented | `/workspace`, studio courses, review center | Course/content authoring, review, artifacts, products, project pipeline. | Needs content-first IA; currently shares generic workspace nav. |
| Instructor | Partially implemented | `/workspace`, sections | Manage sections/cohorts and workspace access. | No distinct instructor dashboard or workflow copy. |
| Parent/guardian | Partially implemented | registration only; backend org role | Can register as parent and create family org intent. | No parent dashboard, learner visibility, or family workflows. |
| Viewer | Backend enum only | None verified | Enum exists. | No frontend routes or permissions. |
| Super admin | Partially implemented | backend privileged; inconsistent frontend | Backend org bypass and V2 creator role. | Frontend creator role constants omit `super_admin`; admin IA unclear. |

## Capability Matrix

| Capability | Student | Teacher | Instructor | Content admin | Org admin | Admin | Parent | Super admin |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Sign in / JWT session | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Register account | Yes | Yes | Yes | No explicit option | No explicit option | No explicit option | Yes | No |
| Create organization | Family/personal intent | School intent | School intent | Via org admin routes if invited | Yes | Not primary | Family intent | Backend capable |
| Switch active org | If member | Yes | Yes | Yes | Yes | Yes | If member | Yes |
| Browse courses/products | Yes | Yes | Yes | Yes | Yes | Yes | Not dedicated | Yes |
| Enroll self | Yes | No | No | No | No | No | No | No |
| Start/continue governed lesson | Yes | Preview/demo | Preview/demo | Preview/demo | Preview/demo | Preview/demo | No | Preview/demo |
| Submit assessment | Yes | Preview only | Preview only | Preview only | Preview only | Preview only | No | Preview only |
| View own progress | Yes | No | No | No | No | No | Future | No |
| View class progress | No | Yes | Yes | Maybe via workspace | Yes | Yes | Future child visibility | Yes |
| Manage sections/classes | No | Yes | Yes | No | Yes | No unless admin route added | No | Yes |
| Assign courses | No | Yes | Likely | No | Possible via section context | Yes | No | Yes |
| Create/edit courses | No | Yes | No verified | Yes in studio | Yes in studio | Yes | No | Yes |
| Publish/review content | No | Readiness visible | No verified | Yes | Yes | Yes | No | Yes |
| Manage users | No | Student list only | Roster only | No | Invites only | Yes | No | Yes |
| Manage badges | No | No | No | No | No | Yes | No | Yes |
| Manage access grants | No | Yes | Yes | Yes | Yes | Yes | No | Yes |
| Discussion/community | API exists | API exists | API exists | API exists | API exists | API exists | Future | API exists |

## Critical Permission Evidence

- `PermissionsService.buildPermissions()` grants workspace navigation to admin, teacher, content_admin, org_admin, and instructor.
- `RoleGuard` checks `PermissionsService.hasAnyRole()`, combining JWT role and active organization role.
- Backend `require_roles()` checks global user role.
- Backend `require_org_roles()` checks active org membership and allows super admin bypass where implemented.
- `backend/app/api/routes/v2_platform.py` defines `CREATOR_ROLES = {"admin", "teacher", "content_admin", "org_admin", "instructor", "super_admin"}` while frontend `creatorRoles` excludes `super_admin`.

## Design Recommendation

Use role-aware entry surfaces, not one shared workspace:

- Student: Learn.
- Teacher/instructor: Teach.
- Content admin: Studio.
- Org admin: Organization.
- Admin/super admin: Admin.
- Parent: Future Family Portal until implemented.

Keep backend role strings unchanged. Add frontend IA grouping over existing routes first.
