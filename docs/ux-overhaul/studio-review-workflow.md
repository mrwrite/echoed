# Studio Review Workflow

Date: 2026-07-13

## Reviewable entities and states

| Entity | Read source | Supported states | Action API | Learner impact |
| --- | --- | --- | --- | --- |
| Artifact/content draft | `GET /api/review-center` | `draft`, `in_review`, `approved`, `rejected`, `needs_changes` | `PATCH /api/artifacts/{id}/review-status` | None directly; artifact is not a runtime lesson |
| Product/learning-offering wrapper | `GET /api/review-center` | `draft`, `in_review`, `approved`, `published`, `archived` | `PATCH /api/products/{id}/review-status` | Wrapper state only; public visibility uses separate publish API |
| Course lesson governance | Review-center composed item | blocked/readiness warning context | Read only in canonical Studio | Existing lesson governance remains authoritative |

V2 creator roles can submit mutations when their workspace is visible and manageable. The API does not distinguish submitter, reviewer, or approver roles and has no final-approver separation.

## Production behavior

- `/studio/review` separates content drafts, learning offerings, and lesson governance.
- Every state mutation requires confirmation naming the item and consequence.
- The displayed state changes only after API success.
- Failure leaves the decision dialog open and states that no change occurred.
- Publishing is omitted from review-state controls and handled separately with public-visibility confirmation.
- Lesson governance remains read-only because content-admin lesson editing is not supported.

## Unsupported workflow

There is no reviewer assignment, review submission timestamp, owner/editor identity, comment thread, request-changes message, attributable activity history, or audit record. The `recent_activity` placeholder is not presented as an audit log.
