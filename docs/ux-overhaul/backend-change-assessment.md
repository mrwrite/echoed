# Backend Change Assessment

## Required Backend Changes

None verified during the design phase.

The redesign can begin frontend-first using existing APIs for:

- Auth and registration: `/api/auth/token`, `/api/auth/register`.
- Session/org context: `/api/orgs`, `/api/orgs/{id}/switch`.
- Curriculum: courses, units, lessons, activities.
- Learning runtime: start-course, progress segment, segment complete.
- Assessment and certifications.
- Sections, roster, assignments.
- Analytics and governance summary.
- V2 workspace: products, projects, sources, artifacts, review center, access grants.
- Uploads and storybook/coloring/badge media.
- Posts and threads.

## Optional Backend Changes

| Change | Classification | Reason |
| --- | --- | --- |
| Current-user/session summary endpoint | Optional | Could reduce token/org bootstrap complexity, but current services work. |
| Preferred landing space preference | Optional | Could persist multi-role default; current preferences may be extended later. |
| Parent/guardian child progress APIs | Required only for parent portal | Parent role is partial; do not expose full parent dashboard without backend relationship/access model. |
| Moderation/flagging endpoints | Required only for full moderation UI | Posts/threads exist, but moderation status was not verified. |
| Asset library list/delete APIs | Optional | Upload exists; admin asset management may need browse/delete later. |
| Server-side search/filter/pagination | Optional | Can begin client-side; may be needed for scale. |
| Non-destructive archive/deactivate endpoints | Optional/preferred | Safer than delete for users/courses if current API only deletes. |

## Backend Changes Avoided

- No duplicate authentication system.
- No duplicate organization onboarding.
- No new role/permission model.
- No parallel progress/session tracking.
- No duplicate course/lesson/assignment/section models.
- No database schema changes in design phase.
- No API shape changes hidden inside the UX redesign.
