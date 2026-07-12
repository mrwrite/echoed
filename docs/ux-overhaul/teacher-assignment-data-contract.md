# Teacher Assignment Data Contract

Date: 2026-07-12

## Existing Assignment Model

| Field | Source | Supported in UI | Notes |
| --- | --- | --- | --- |
| Assignment ID | `AssignmentResponse.id` | Display/list only | UUID, not exposed as primary UI label. |
| Section/class target | URL section ID and `section_id` | Yes | Class-first workflow. |
| Target type | `target_type` | Yes | UI supports `course`, `unit`, and `lesson`; backend enum must accept the chosen value. |
| Target ID | `target_id` | Yes | Course picker is available for `course`; unit/lesson still require IDs because no picker endpoint was verified. |
| Due date | `due_at` | Yes | Uses `datetime-local`; backend receives ISO-like browser value through Angular binding. |
| Instructions | `instructions` | Yes | Preserved after recoverable failures. |
| Created by | `created_by` | Not shown | Internal teacher identifier not exposed. |
| Created at | `created_at` | Available | Used for ordering only when needed. |
| Assigned learners | Not in current assignment create response | No | Class assignment endpoint does not support individual learner selection. |
| Status/publishing state | Not exposed | No | UI does not invent draft/published states. |
| Completion/review state | Submission model exists separately | Limited | No teacher-facing per-learner completion endpoint verified. |
| Retry/reassignment | Not exposed | No | Not implemented. |
| Edit/delete/archive | No endpoint verified | No | UI does not show destructive assignment actions. |
| Notifications | No endpoint verified | No | UI does not claim notifications are sent. |

## Creation Behavior

The class detail assignment tab uses:

- Required target validation.
- Optional due date and instructions.
- Confirmation dialog before assignment creation.
- Duplicate-submit prevention while saving.
- Persistent inline error if creation fails.
- Success toast only after API confirmation.

Known limitation: the API creates section-wide assignments only; the UI states that individual learner selection is not supported by the current endpoint.
