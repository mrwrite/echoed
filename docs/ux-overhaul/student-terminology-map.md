# Student Terminology Map

Date: 2026-07-11

Visible student copy now prefers learning language while preserving technical route/API names.

| Internal or legacy term | Student-visible term | Notes |
| --- | --- | --- |
| Product | Course, available learning | `/learn/products` remains as a transitional route/API-backed surface. |
| Learner product | Course-backed learning | API name unchanged. |
| Workspace | Learn | Student navigation does not expose `/workspace` as a normal destination. |
| Artifact | Resource | Not used in student course journey. |
| Pipeline | Course path, learning path | No student-facing pipeline copy added. |
| Launch | Start, continue, resume | Course actions use learning verbs. |
| Consumption | Learning, progress | Avoided. |
| Certification | Certificate, earned certificate | Avoids overstating external accreditation. |
| Badge | Badge | Kept distinct from certificate. |
| Course completion | Course complete | Kept distinct from certificate. |
| Segment | Lesson progress, governed lesson | Internal `unit_progress_id` remains hidden from learners. |

## Remaining Technical Terms

- `/learn/products` remains the route path for compatibility.
- `LearnerProduct` remains a frontend model/API wrapper.
- `unit_progress_id` remains the internal identifier for `/learn/lesson/:id`.
