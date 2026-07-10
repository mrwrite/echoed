# Information Architecture

## IA Principles

- Start from role intent, not internal product modules.
- Keep learners in a simple Learn space.
- Keep educators in a Teach space focused on classes, assignments, learner support, and curriculum preview.
- Keep content operations in Studio.
- Keep org/user/platform administration in Admin.
- Preserve existing backend resources and introduce route aliases or frontend grouping incrementally.

## Proposed Top-Level Spaces

| Space | Primary users | Purpose | Existing routes reused |
| --- | --- | --- | --- |
| Learn | Student | Resume assigned learning, browse available learning, complete lessons, track achievements. | `/learn`, `/learn/products`, `/learn/paths`, `/learn/certificates`, `/learn/resources`, `/learn/lesson/:id`. |
| Teach | Teacher, instructor | Manage classes, assignments, learner support, curriculum preview. | `/home/sections`, `/home/sections/:id`, `/home/courses`, `/home/assessments/:id`, `/home/lesson/:id`, teacher dashboard logic. |
| Studio | Content admin, org admin, curriculum creator | Projects, sources, artifacts, product/course authoring, review center. | `/workspace/projects`, `/workspace/product-studio`, `/workspace/knowledge-sources`, `/workspace/artifacts`, `/workspace/review-center`, `/workspace/products`. |
| Organization | Org admin | Members, invites, access, org settings, classes overview. | `/workspace/settings/invites`, `/workspace/access`, `/home/org/invites`, `/home/sections`. |
| Admin | Admin, super admin | Users, courses, badges, reporting, moderation, platform settings. | `/home/admin/users`, `/home/admin/courses`, `/home/admin/badges`, `/workspace/analytics`. |
| Community | Authenticated roles | Discussions, shared resources, community contribution. | Existing posts/threads APIs, `/workspace/commercial` as temporary route alias. |

## Contextual Navigation

- Course/product detail: Overview, Content, Learners/Access, Review, Analytics, Settings.
- Class detail: Overview, Roster, Assignments, Progress, Discussion.
- Lesson player: Content, Activity, Notes, Progress; teacher preview adds Facilitation Notes.
- Admin user detail: Profile, Roles, Organizations, Activity, Danger Zone.

## Default Landing Rule

Suggested frontend-only default after bootstrap:

1. Student-only users: `/learn`.
2. Teacher/instructor without content/admin role: `/teach` alias to current teacher dashboard/classes.
3. Content admin: `/studio`.
4. Org admin: `/organization`.
5. Admin/super admin: `/admin`.
6. Multi-role users: show role switcher with clear destinations and remember preferred mode using existing preferences.

Initial implementation can preserve physical route paths while changing navigation labels and redirect decisions.
