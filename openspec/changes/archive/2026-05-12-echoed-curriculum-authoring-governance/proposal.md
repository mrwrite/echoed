## Why

EchoEd now has governed learner delivery, lesson readiness checks, assessment/mastery foundations, and a flagship pathway, but it still lacks a scalable institutional workflow for authoring, reviewing, approving, publishing, versioning, and maintaining curriculum safely. This change defines that governance layer so future pathways can be expanded without breaking learner-safe delivery, assessment integrity, or the platform's bounded UX model.

## What Changes

- Add a canonical curriculum authoring lifecycle that governs draft, review, approved, and published states for course, unit, lesson, and aligned assessment content.
- Define additive publish-readiness and validation rules for academic quality, source coverage, deterministic ordering, learner-safe visibility, and staff preview boundaries.
- Add bounded versioning and maintenance rules for published curriculum, including draft revisions, material-change handling, archival/deprecation semantics, and historical learner-progress safety.
- Define bounded educator and content-admin authoring UX expectations such as review queues, readiness indicators, missing-field guidance, and compliance warnings without expanding into a heavy LMS suite.
- Extend governance expectations for assessment alignment, learner availability gating, evidence preservation, and readiness compatibility across pathways.
- Keep the implementation on the existing Course, Unit, Lesson, Activity, Source, lesson governance, assessment/mastery, and governed delivery architecture with no parallel curriculum system.

## Capabilities

### New Capabilities
- `authoring-workflow-governance`: Role-based draft, review, approved, and published workflow governance for curriculum content.
- `pathway-course-publishing-governance`: Publish-readiness, learner availability, staff preview, and deterministic ordering rules for pathway, course, unit, and lesson publishing.
- `curriculum-versioning-and-maintenance`: Additive versioning, revision, archival, and maintenance rules that preserve historical learner safety.
- `authoring-ux-boundaries`: Bounded educator and content-admin authoring UX expectations, readiness indicators, review surfaces, and compliance guidance.
- `assessment-alignment-governance`: Governance rules for assessment readiness, competency alignment, learner availability gating, and historical evidence preservation.
- `multi-pathway-curriculum-governance`: One canonical governance approach that scales across flagship, academic, STEM, GED/adult, and enrichment pathways.
- `curriculum-governance-technical-alignment`: Architectural constraints that preserve existing content, delivery, assessment, auth, and UX foundations.
- `curriculum-governance-verification`: Regression and verification expectations for readiness, publishing, learner-safe visibility, published edits, preview behavior, and no learner-progression corruption.

### Modified Capabilities

- None.

## Impact

- Affected areas will likely include lesson governance rules, curriculum serialization, publishing/readiness contracts, educator/content-admin authoring surfaces, assessment readiness checks, and focused backend/frontend regression coverage.
- No rewrite of Course, Unit, Lesson, Activity, or Source is required.
- No new learner progression system, separate authoring database, public creator marketplace, or AI content generation workflow is introduced.
