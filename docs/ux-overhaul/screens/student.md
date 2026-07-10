# Student Screen Specifications

## Student Dashboard / Learn Home

- Route/component: proposed canonical `/learn`, current `LearnerPortalComponent` and `StudentViewComponent`.
- Goal: know what to do next.
- Main action: continue assigned/current lesson.
- Information order: next learning, assignments, progress, achievements, available courses, resources.
- Desktop: two-column with next action and progress side panel.
- Mobile: single-column; next action first; bottom nav.
- API: `/api/student-courses`, `/api/analytics/student-progress`, `/api/students/{id}/badges`, `/api/programs`, `/api/students/me/certifications`, `/api/learner-portal/products`.
- States: loading dashboard, no assigned learning, all complete, partial API failures, permission denied.
- Backend changes: none.

## Course Library / Available Learning

- Routes: `/learn/products`, `/home/courses`.
- Goal: browse available learning.
- Actions: search/filter, open course, enroll/start.
- API: `/api/courses`, `/api/learner-portal/products`, `/api/enroll`.
- Empty: explain no available courses.
- Error: retry.
- Accessibility: card headings, status text, no color-only progress.

## Course Overview

- Current: course details through `AvailableCoursesComponent` and course models.
- Goal: understand course structure before starting.
- Layout: overview, units, lessons, estimated time, progress, source/cultural context.
- API: `/api/courses/{id}`, `/api/start-course`.
- Backend changes: optional if estimated time/source context is not available.

## Unit Overview

- Current: implicit in course/lesson data.
- Goal: understand lesson sequence and unlock/progress.
- API: `/api/courses/{id}`, progress data.
- Backend changes: none for basic structure.

## Lesson Player

- Route/component: `/learn/lesson/:id` or `/home/lesson/:id`, `LessonViewComponent`.
- Goal: complete lesson safely.
- Main action: complete lesson segment.
- Secondary actions: exit, retry load, view activity, teacher feedback if returned.
- API: `/api/progress/segment`, `/api/lessons/{id}`, `/api/progress/segment/complete`.
- States: resolving segment, governed unavailable, pending review, completed, stale segment recovery, generic error.
- Desktop: content column, progress/lesson outline side panel.
- Mobile: single-column, sticky action bar, safe exit.
- Accessibility: live region for save/next segment, heading order, keyboard activity controls.
- Backend changes: none.

## Activity and Assessment

- Route/component: `/home/assessments/:id`, `AssessmentDetailComponent`; activities in `LessonViewerComponent`.
- Goal: answer and submit work.
- API: `/api/assessments/{id}`, `/api/assessments/{id}/attempts`.
- States: unavailable, loading, submit pending, submit failed, completed feedback.
- Accessibility: form labels, grouped options, error association.

## Progress and Achievements

- Current components: student dashboard, certifications, badges.
- Goal: see growth and earned recognition.
- API: `/api/analytics/student-progress`, `/api/students/{id}/badges`, `/api/students/me/certifications`.
- Layout: progress summary, course progress, badges, certificates, timeline.
- Backend changes: none.

## Discussions

- Current: backend posts/threads APIs; no clear student discussion screen verified.
- Proposed: moderated class/course discussion.
- API: `/api/threads`, `/api/posts`.
- Backend changes: optional moderation/flagging if not present.

## Profile and Settings

- Route/component: `/home/me/preferences`, `PreferencesComponent`.
- Goal: preferences and profile.
- API: `/api/me/preferences`.
- Backend changes: none.
