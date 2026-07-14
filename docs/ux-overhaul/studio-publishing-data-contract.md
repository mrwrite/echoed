# Studio Publishing Data Contract

Date: 2026-07-13

## Terms that are not interchangeable

| Term | Verified meaning |
| --- | --- |
| Draft | Wrapper/content record is still being prepared. |
| In review | Wrapper review decision is pending. |
| Approved | Wrapper review status is approved; this alone does not create public visibility or publish lessons. |
| Published | V2 product wrapper has been published; public discovery also requires `visibility: public`. |
| Archived | Wrapper review/status value; no dedicated reversible archive endpoint exists. |
| Learner-visible lesson | Controlled separately by lesson review/readiness and governed runtime APIs. |
| Teacher-visible | No separate V2 wrapper field or verified Studio control exists. |
| Organization scope | V2 records are restricted to workspaces visible through active organization membership. |

## Supported publishing mutation

`PATCH /api/products/{product_id}/publish` accepts a supported visibility other than draft/archived. It sets wrapper status to `published`, may move review state to `approved`, creates a slug, and records publishing/update timestamps.

It does not publish legacy CourseVersion content, override lesson readiness, enroll a learner, create progress, or grant access.

## Studio behavior

- `/studio/publishing` lists current wrapper states and visibility.
- Publishing is initiated from `/studio/content/:productId`.
- Confirmation states the public scope and what remains unchanged.
- UI state updates only from the successful API response.
- Failed publishing leaves the prior state visible.
- A public preview link appears only after the returned wrapper is published and has a slug.

## Unsupported behavior

There is no V2 unpublish endpoint, scheduled publish, dependency-validation response, organization-specific publishing mutation, rollback, or publishing audit. Studio therefore exposes no unpublish or schedule control.
