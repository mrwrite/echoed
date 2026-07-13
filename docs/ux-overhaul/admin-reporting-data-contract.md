# Admin Reporting Data Contract

Date: 2026-07-13

Source: `GET /api/analytics/overview`, authorized for `admin` only.

| Metric | Definition |
| --- | --- |
| Students | Users whose platform role equals `student`. |
| Teachers | Users whose platform role equals `teacher`; instructors are not included. |
| Courses | All course records. |
| Active students | Distinct student IDs with an enrollment record; this is not time-window activity. |
| Total enrollments | All `StudentCourse` records. |
| Incomplete enrollments | Total enrollments minus completed enrollment records. The backend field is `pending_enrollments`; UI avoids implying an invitation/approval state. |
| Lessons completed | Completed `SegmentProgress` records. |
| Units completed | Completed `StudentUnitProgress` records. |
| Courses completed | `StudentCourse` records with status `completed`. |
| Course completion rate | Completed course enrollments divided by total enrollments, rounded by backend. |

The report does not claim trends, active account state, engagement, growth, organization comparison, audit events, or time ranges. Workspace/V2 analytics remain Studio reporting and are not merged into Admin.
