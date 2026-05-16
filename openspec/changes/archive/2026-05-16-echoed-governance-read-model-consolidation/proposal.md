## Why

EchoEd now has publish-readiness governance, safe-publish validation, historical lineage safety, staff lineage visibility, competency evidence integrity, runtime intervention intelligence, governed learner delivery, and premium staff UX primitives, but staff-facing course governance still has to be assembled from multiple per-course reads. This change is needed now to define one bounded, deterministic, read-only governance summary architecture so staff dashboards can consume a single course payload without introducing a new workflow, mutating state, or changing learner-facing contracts.

## What Changes

- Add one unified course governance summary contract that aggregates publish readiness, safe-publish validation, lineage safety visibility, competency evidence integrity, and runtime intervention recommendation context into a single staff-readable payload per course.
- Define a shared backend read-model composition boundary so existing deterministic validators remain the source of truth while route-level orchestration duplication is reduced.
- Define staff dashboard consumption rules so admin and teacher governance surfaces can request one course-level governance payload while preserving the current bounded sections and avoiding workflow/action expansion.
- Preserve existing staff/admin/content authorization boundaries, explicitly deny learner/student access to the summary contract, and keep learner-facing governed delivery and serialization unchanged.
- Define performance and scale expectations for course-by-course reads, batching, pagination, and future caching boundaries without introducing complex caching in this change.
- Add focused verification expectations for combined payload shape, staff access, learner denial, read-only behavior, no progression mutation, no assessment/certification/reporting mutation, frontend request reduction, and continued correctness of individual validators.
- Keep the work additive to the existing governance, versioning, lineage, competency, runtime support, and premium UX architecture rather than introducing a publish workflow, rollback workflow, CMS rewrite, grading workflow, intervention workflow, learner-facing behavior, or mutation endpoint.

## Capabilities

### New Capabilities
- `course-governance-summary-read-model`: Defines the canonical aggregated staff-facing course governance payload and its deterministic composition boundaries.
- `governance-read-model-service-boundary`: Defines the shared backend read-only composition layer, batching expectations, and non-mutation constraints for governance summary assembly.
- `governance-read-model-dashboard-consumption`: Defines how existing staff/admin dashboard surfaces consume one bounded governance payload per course without expanding workflow controls.
- `governance-read-model-verification`: Defines regression expectations for aggregate payload shape, authorization, read-only safety, frontend request reduction, and validator preservation.

### Modified Capabilities
- `pathway-course-publishing-governance`: Extend course publish-readiness requirements so staff-facing governance can expose aggregate readiness inside the unified summary payload.
- `safe-published-editing`: Extend safe-publish warning requirements so deterministic revision-safety results can be exposed inside the unified course governance summary.
- `staff-lineage-safety-visibility`: Extend lineage and historical-safety visibility requirements so they can participate in a shared course governance summary contract.
- `staff-competency-integrity-visibility`: Extend competency evidence and mastery-integrity visibility requirements so they can participate in the unified governance summary payload.
- `educator-runtime-intervention-intelligence`: Extend educator/staff runtime recommendation visibility requirements so intervention guidance can be included in the same bounded course governance summary.
- `versioning-ux-and-governance-boundaries`: Extend bounded staff governance UX requirements so existing sections can be preserved while consuming one aggregated course payload instead of multiple per-course requests.

## Impact

- Affected backend areas will likely include existing staff/admin governance routes or serializers, read-only validator helpers for publish readiness, safe publish, lineage safety, competency evidence integrity, and runtime intervention guidance, plus shared schema/read-model composition code.
- Affected frontend areas will likely include existing staff/admin governance dashboards and their current per-course request fan-out behavior.
- Existing learner-facing contracts, governed delivery behavior, progression semantics, assessment evidence storage, certification/reporting interpretation, and mutation workflows remain unchanged.
- No new mutation endpoint, workflow engine, rollback system, CMS rewrite, grading engine, or complex cache layer is introduced.
