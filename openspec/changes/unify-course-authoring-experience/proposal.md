## Why

EchoEd currently splits course creation across a shallow Studio draft form and a legacy four-step editor whose routes and APIs exclude the content-administrator roles expected to own authoring. A unified, low-friction course studio is needed so permitted creators can safely build, review, preview, and submit complete courses without navigating conflicting workflows or risking lost and duplicate drafts.

## What Changes

- Establish one canonical course-authoring entry point for content administrators, organization administrators, teachers or instructors, reviewers, and platform administrators, with actions determined by explicit role and organization scope.
- Replace the disconnected shell-creation and legacy wizard experiences with a resumable course studio covering setup, outline, lesson and activity construction, quality checks, learner preview, review submission, and governed publishing.
- Add real draft semantics: autosave, visible save state, exit-and-resume behavior, duplicate-submission protection, recoverable failures, and version-aware edits.
- Add guided course setup for audience, subject, age or grade range, locale, learning objectives, skills, and standards metadata using existing canonical course structures.
- Add an editable course outline with inline unit, lesson, and activity creation; deterministic ordering; duplication; and accessible non-drag reordering controls.
- Integrate validation, objective alignment, accessibility guidance, governance readiness, and learner preview before review or publication.
- Add templates, course duplication, and a bounded import/export foundation, including a path toward Common Cartridge and QTI interoperability without making external standards a prerequisite for the first implementation slice.
- Preserve one canonical curriculum hierarchy and learner-delivery governance model; no parallel course, unit, lesson, activity, review, or publishing system will be introduced.

## Capabilities

### New Capabilities

- `course-authoring-experience`: Defines the unified, role-aware, accessible, autosaving course-studio workflow and its authoring, quality, preview, and recovery behavior.

### Modified Capabilities

- `course-and-lesson-api-contracts`: Extends authoring-capable course and lesson contracts so permitted organization-scoped creators can create and update the complete canonical course graph through consistent APIs.
- `role-based-content-visibility`: Defines distinct author, reviewer, publisher, and oversight actions while preserving learner-safe and educator-only field visibility.
- `pathway-course-publishing-governance`: Integrates draft lifecycle, preview, readiness feedback, review submission, versioning, and permission-controlled publication into the authoring workflow.

## Impact

- Frontend: Angular workspace and Studio routes, course listing and editor surfaces, course wizard/service code, shared forms, status messaging, responsive behavior, and accessibility tests.
- Backend: existing course routes, schemas, organization-role dependencies, course-version and governance services, nested course-graph update behavior, and audit-safe publishing endpoints.
- Data: canonical course, unit, lesson, activity, source, version, organization, and governance records remain authoritative; migrations may be required only for explicit draft ownership, autosave revision, or template metadata not already represented.
- Tests: role-matrix API coverage, nested graph persistence, draft/version behavior, validation, keyboard and non-drag interactions, full author journeys, preview isolation, review submission, and safe publish behavior.
- Interoperability: establishes extension points for Common Cartridge course exchange and QTI assessment exchange; initial implementation must not claim certification without conformance testing.
