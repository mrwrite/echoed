# Teacher Screen Specifications

## Teacher Dashboard / Today

- Current: `TeacherViewComponent`.
- Goal: orient to current class priorities.
- Main action: open learners needing support or recent submissions.
- API: `/api/courses`, `/api/users/students`, `/api/analytics/teacher-summary`, runtime support/governance endpoints.
- Layout: today priorities, class cards, learner support, recent submissions, curriculum quick links.
- Mobile: priorities first, tabs for support/classes/curriculum.
- Backend changes: none.

## Sections / Classes

- Routes/components: `/home/sections`, `/workspace/learners/cohorts`, `SectionsComponent`.
- Goal: create/manage class.
- API: `/api/sections`.
- Layout: class list with roster count, active assignments, mode, recent activity.
- Empty: create first class.
- Backend changes: none.

## Class Detail

- Route/component: `/home/sections/:id`, `SectionDetailComponent`.
- Goal: manage roster, assignments, progress.
- API: `/api/sections/{id}/roster`, `/api/sections/{id}/assignments`, `/api/sections/{id}/analytics/summary`.
- Tabs: Overview, Roster, Assignments, Progress, Discussion.
- Mobile: tabs become segmented control.
- Backend changes: none for existing roster/assignment; optional for richer learner detail.

## Curriculum Library and Course Preview

- Routes/components: `/home/courses`, course detail/wizard preview.
- Goal: find curriculum and preview before assigning.
- API: `/api/courses`, `/api/courses/{id}`, governance summary.
- Layout: filters by grade/topic/status, course cards, preview drawer.
- Backend changes: optional search/filter endpoints later.

## Assignment Creation

- Current: section assignments API; UI in section detail.
- Goal: assign learning to class or learners.
- API: `/api/sections/{id}/assignments`, `/api/assign-course`.
- Flow: choose content, choose learners, due date/status, review, confirm.
- Validation: required class/content/target.
- Backend changes: none for basic assignment.

## Learner Progress and Student Detail

- Current: teacher summary and runtime support.
- Goal: identify and support learners.
- API: `/api/analytics/teacher-summary`, educator runtime support, student course/progress endpoints where available.
- Layout: support states, evidence basis, recent activity, next action.
- Backend changes: optional student detail aggregation endpoint.

## Review and Feedback

- Current: assessment attempts exist; explicit review UI unclear.
- Proposed: submissions queue and feedback panel.
- API: assessments/assignments submission routes.
- Backend changes: optional if feedback persistence is incomplete.

## Discussion Moderation

- Current: posts/threads APIs.
- Proposed: class discussion tab with teacher moderation.
- Backend changes: optional moderation flags if not present.

## Teacher Settings

- Route/component: preferences.
- API: `/api/me/preferences`.
