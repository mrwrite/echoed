# Teacher Review Behavior

Date: 2026-07-12

## Assessment and Work Review Findings

| Behavior | Verified support | Evidence |
| --- | --- | --- |
| Teachers can load assessment details | Yes | `GET /api/assessments/{id}` includes questions for staff users. |
| Students can submit assessment attempts | Yes | `POST /api/assessments/{id}/attempts` requires `student`. |
| Auto-scoring | Yes | Assessment submit endpoint scores answers and records events. |
| Teachers can list work needing review | Not verified | No teacher review queue endpoint found for student assignment submissions. |
| Teachers can manually score | Not verified | No score mutation endpoint for teachers found. |
| Teachers can comment/save feedback | Not verified | No feedback persistence endpoint found. |
| Teachers can publish/return feedback | Not verified | No return-work endpoint found. |
| Retries can be granted | Not verified | Assessment max attempts exist, but no teacher retry grant endpoint found. |
| Correct answers visible to staff | Partial | Staff assessment serialization includes questions; answer visibility is model-dependent. |
| Rubric support | Not verified | No rubric endpoint surfaced. |

## UI Decision

Teach surfaces describe work review and feedback as unavailable unless the current API confirms a supported action. No toast-only confirmation, manual grading state, returned-work state, or retry state was invented.
