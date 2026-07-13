# Platform Admin Production Audit

Date: 2026-07-13

## Authorization Summary

The platform role stored on `User.role` is the backend authority. `require_roles()` performs exact string matching and does not implement inheritance. Organization roles are separate `OrganizationMembership.role` values. Frontend permissions and hidden navigation are presentation only.

`admin` is the only role authorized for the current user directory, user updates/deletion, Admin overview analytics, course list/detail/write operations, badge creation/assignment, and badge image upload. `super_admin` is not an alias for `admin`: it can bypass organization-name update membership checks and can read unscoped V2 analytics, but it is rejected by the core Admin endpoints above. The current shell previously displayed an Admin area for both roles while legacy Admin routes allowed only `admin`.

## Route And Screen Audit

| Current route or surface | User goal | Authorized role from backend | APIs | Sensitivity | Current actions | Backend enforcement | UX, accessibility, and responsive risks | Recommendation / owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `/home` Admin dashboard | Assess platform state | `admin`; `super_admin` cannot call its core APIs | `GET /api/analytics/overview`, `/api/users`, `/api/courses`, course governance endpoints | Platform user counts; learner recommendations | Read summaries; legacy page also deletes users/courses | Exact role checks for lists; governance allows staff roles | 546-line dashboard mixes operational oversight, learner intervention data, and destructive actions; partial failures are difficult to distinguish; dense mobile layout | Canonical `/admin`; Admin. Keep `/home` as a legacy landing until dynamic compatibility routing is retired. |
| `/home/admin/users` | Review and manage accounts | `admin` | `GET /api/users`, `DELETE /api/users/{id}` | Names, email, username, role, created date; API also serializes hashed password unless excluded by ORM serialization | Immediate delete | Exact `admin` check; delete cascades posts, threads, badges, unit links and user | No loading/error/empty state, no confirmation, no search/filter, raw role text, table overflows mobile | Canonical `/admin/users`; Admin. Minimize visible fields and require exact destructive confirmation. |
| No user-detail route | Inspect one account and change role | `admin` | `GET/PUT /api/users/{id}` | Identity, email, role | Full DTO update; role change possible | Exact `admin` check; no role allowlist, final-admin protection, or self-lockout protection | Missing UI; PUT requires complete identity DTO and optional empty password convention | Add `/admin/users/:userId`; Admin. Allow verified role changes except self-change; confirm privilege changes; document backend gaps. |
| `/workspace/learners/users` | Duplicate user list | `admin` | Same as user list | Same | Same | Same | Duplicate namespace suggests organization ownership | Keep as compatibility route; canonical `/admin/users`; Admin. |
| `/home/admin/courses` | Oversee courses | `admin` for list/write | `GET/DELETE /api/courses`, course governance endpoints | Curriculum metadata and learner-facing availability | Legacy create/edit/delete | Exact `admin`/`teacher` on core course CRUD | “Product” language, authoring controls mixed into Admin, immediate delete, no states, table overflows | Canonical `/admin/courses`; Admin oversight only. Link to detail oversight; keep authoring out of Admin. |
| `/workspace/products/manage` | Duplicate course management | `admin` | Same as course list | Same | Same | Same | Duplicates Admin and Studio concepts | Compatibility alias only; canonical `/admin/courses`; Admin. |
| `/home/admin/badges` | Create and inspect badges | Read: any authenticated user; create/upload/assign: `admin` | `GET/POST /api/badges`, `POST /api/upload/badge`, assignment endpoint | Public recognition metadata and images | Create and upload | Explicit `admin` checks on writes | Missing load/error/empty/submission states; inaccessible image; file restrictions not explained; no edit/delete API exists | Canonical `/admin/badges`; Admin. Create supported; existing badges read-only. |
| `/workspace/settings/badges` | Duplicate badge management | Route says `admin` | Same as badge list | Same | Same | Same | Wrong settings ownership | Compatibility alias only; canonical `/admin/badges`; Admin. |
| `/workspace/analytics` | Review workspace/content analytics | Several staff roles including `super_admin` | V2 analytics endpoints | Organization/workspace aggregate operational data | Read only | Exact role list plus workspace scoping; admins/super admins unscoped | Content/Studio reporting is not the same as platform Admin reporting | Keep in Studio. Add `/admin/reports` using only `/analytics/overview` for `admin`; no cross-link for `super_admin` unless definitions match. |
| `/workspace/commercial` | Community project surface | Creator roles | V2/community APIs | Community operational data | Varies | Creator-role route checks | Not moderation and not Admin oversight | Community owner; remove from Admin navigation. Preserve route. |
| `/workspace/settings` | Preferences/settings | Creator roles | Preferences APIs | User preferences | Edit preferences | Existing auth | Exposed as “Platform settings” without a platform-settings API | Keep as user/Studio settings; omit from Admin navigation. |
| `/workspace/review-center` | Content review | Creator roles | V2 review APIs | Content review state | Content workflow actions | Creator-role checks | Belongs to Studio; not platform moderation | Studio owner; do not migrate. |
| `/workspace/access` | Product access grants | Creator roles | V2 access-grant APIs | Learner access | Grant/revoke | V2 role and workspace checks | Organization/content access, not platform account access | Organization/Studio owner; do not migrate. |
| Organization selector/header | See organizations for current account | Any authenticated user | `GET /api/orgs` | Organization identity, current membership role | Switch active organization; create organization elsewhere | List is restricted to current user's memberships; PATCH allows member content/org admin or platform `super_admin` | Cannot provide platform-wide oversight, counts, members, admins, sections, or invitations | Add `/admin/organizations` as explicitly scoped read-only membership visibility. Detail is limited to returned organization metadata. Admin owner for visibility; self-service remains Organization. |
| Threads/posts routes | Discuss or mutate community content | No authentication dependency | CRUD `/api/threads`, `/api/posts` | User-generated content and author identifiers | Create/update/delete | No authentication, scope, ownership, moderation role, report, restore, lock, or audit behavior | Unsafe for platform moderation; deletion irreversible and unscoped | No Admin route. Document as backend security/moderation gap; Community future change. |
| Upload routes | Upload lesson assets | Badge upload: `admin`; coloring/storybook: `admin` or `teacher` | `/api/upload/*` | Uploaded files | Create file | Exact role checks | No asset list, metadata, delete, ownership, or moderation APIs | Badge upload stays inside badge creation. No Admin asset library. |

## Destructive Behavior

- User deletion permanently removes the user plus authored posts/threads, student badges, and unit links. The endpoint has no self-delete protection, final-admin protection, audit record, dry run, or restore.
- Course deletion permanently deletes the course through the current CRUD endpoint and has no archive/restore contract.
- Badge deletion, badge edit, organization archive/delete, account disable/restore, invitation resend, role removal, membership management, and platform settings are not supported by verified APIs.

## Route Migration Decision

The canonical family is `/admin`, `/admin/users`, `/admin/users/:userId`, `/admin/organizations`, `/admin/organizations/:organizationId`, `/admin/courses`, `/admin/courses/:courseId`, `/admin/badges`, and `/admin/reports`. Moderation and platform settings routes are omitted. Legacy routes remain guarded aliases; no broad deletion is part of this phase.

## Primary Risks And Mitigations

- **Authorization mismatch:** exact backend role checks remain authoritative; `super_admin` receives only the supported overview limitation state and organization visibility.
- **Privacy:** broad user lists show name, role, and created date only. Email and username are confined to an individual detail view. Password hashes, tokens, and raw identifiers are never rendered.
- **Responsive tables:** lists switch from semantic desktop tables to equivalent mobile records without hiding primary actions.
- **High-impact actions:** shared confirmation names the object, consequence, scope, and irreversibility; UI updates only after API success.
- **Partial failures:** each overview source reports independently so one failed request does not make successful counts appear absent.
