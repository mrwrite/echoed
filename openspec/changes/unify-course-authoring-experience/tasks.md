## 1. Authorization and Existing-System Baseline

- [x] 1.1 Document the initial organization policy for content-admin authoring, org-admin publication, teacher derivative copies, reviewer decisions, and platform-admin oversight in the change design before behavior is enabled.
- [x] 1.2 Add a role-and-organization-scope test matrix covering create, view draft, edit, duplicate, preview, submit, review, publish, and denied mutations.
- [x] 1.3 Inventory canonical course, unit, lesson, activity, source, assessment, version, review, and publication fields and map both existing creation paths to that model.
- [x] 1.4 Add regression tests proving learner course and lesson reads continue to exclude drafts and educator-only fields throughout authoring changes.

## 2. Backend Capability Contract

- [x] 2.1 Implement one reusable backend course-authoring capability resolver based on platform role, active organization membership, course relationship, and organization policy.
- [x] 2.2 Add bounded capability response schemas for create, edit, duplicate, preview, submit, review, and publish actions.
- [x] 2.3 Expose collection-scope and course-scope capabilities through existing course route modules.
- [x] 2.4 Replace direct role checks on authoring mutations with the capability resolver while preserving explicit learner denial.
- [x] 2.5 Add backend tests proving manipulated or stale client capability state cannot authorize a mutation.

## 3. Durable Draft and Aggregate Persistence

- [x] 3.1 Add or migrate draft ownership, organization scope, lifecycle state, revision, save timestamp, and template-origin metadata that are not already represented canonically.
- [x] 3.2 Implement a transactional aggregate authoring service that creates and updates course metadata, ordered units, lessons, activities, sources, and assessment references through existing models.
- [x] 3.3 Implement deterministic order normalization and validation for every nested collection mutation.
- [x] 3.4 Implement idempotent draft creation and test that safe retries return one durable draft.
- [x] 3.5 Implement optimistic revision checks and a structured conflict response that prevents stale overwrites.
- [x] 3.6 Add rollback tests proving invalid nested updates never commit a partial course graph.

## 4. Canonical Authoring APIs and Legacy Convergence

- [x] 4.1 Extend the existing organization-aware authoring routes and schemas to read and persist the complete authoring aggregate and current revision.
- [x] 4.2 Add structured validation issues containing severity, entity type, entity ID, field, message, and corrective context.
- [x] 4.3 Add duplication operations for courses, units, lessons, and activities with regenerated identifiers, preserved attribution, and no inherited enrollment or publication state.
- [x] 4.4 Route retained legacy create and update endpoints through the aggregate service with equivalent authorization, idempotency, validation, and transaction behavior.
- [x] 4.5 Add contract tests for new and legacy routes to prevent graph, permission, and learner-serialization drift during migration.

## 5. Canonical Studio Shell and Navigation

- [x] 5.1 Add typed Angular models and service methods for authoring aggregates, revisions, lifecycle state, capabilities, validation issues, and save conflicts.
- [x] 5.2 Build the canonical responsive course-studio shell with persistent outline, focused editor area, and Setup, Build, Quality, Preview, and Release modes.
- [x] 5.3 Replace hard-coded authoring role arrays with route entry behavior backed by the capability contract and backend enforcement.
- [x] 5.4 Point content-admin, organization-admin, and permitted teacher or admin course entry actions to the canonical Studio routes.
- [x] 5.5 Add loading, permission-denied, not-found, empty, and recoverable route-failure states with logical focus placement.

## 6. Guided Setup and Outline Authoring

- [x] 6.1 Implement blank-course setup for title, description, subject, audience or age or grade range, locale, learning objectives, skills, and standards metadata.
- [x] 6.2 Implement inline unit, lesson, and activity creation and editing against the canonical draft graph.
- [x] 6.3 Implement course, unit, lesson, and activity duplication controls gated by returned capabilities.
- [x] 6.4 Implement deterministic drag-and-drop reordering using the same state operation as keyboard-operable Move up, Move down, and position controls.
- [x] 6.5 Add contextual destructive-action confirmation and ensure removals preserve valid ordering and focus.
- [x] 6.6 Integrate existing media upload, source attribution, assessment references, and supported activity types without introducing duplicate services.

## 7. Autosave, Recovery, and Conflict UX

- [x] 7.1 Implement debounced serialized autosave for durable drafts and an explicit Save now action using revision tokens.
- [x] 7.2 Display Saving, Saved with time, Save failed, Offline, and Conflict states through accessible status messaging.
- [x] 7.3 Retain unsaved client input after save failure and provide a retry path that cannot create a duplicate course.
- [x] 7.4 Implement exit-and-resume behavior and a navigation warning only while local changes are not durably saved.
- [x] 7.5 Implement bounded conflict recovery that lets a creator reload the server version or preserve recoverable local content without silently overwriting either revision.
- [x] 7.6 Add component and service tests for debounce, serialized writes, retries, duplicate prevention, navigation, refresh, and multi-tab conflict responses.

## 8. Quality, Preview, Review, and Publishing

- [x] 8.1 Build progressive field-level validation with text explanations, direct issue links, and focus movement to the first blocking problem.
- [x] 8.2 Build the quality panel by combining completeness, objective alignment, assessment coverage, ordering, accessibility prompts, source and media checks, and canonical governance findings.
- [x] 8.3 Connect issue actions to the affected course, unit, lesson, activity, source, or assessment editor without losing draft context.
- [x] 8.4 Implement staff learner preview using learner-safe serialization of the selected durable draft or version without changing learner availability.
- [x] 8.5 Connect submit-for-review, review feedback and decisions, version history, readiness refresh, and safe publish to existing governance services.
- [x] 8.6 Ensure lifecycle actions render only when capabilities allow them and that automated quality success never bypasses required human review.
- [x] 8.7 Add end-to-end tests proving draft isolation, learner-safe preview, review return, approved publication, and published-version stability during later edits.

## 9. Accessibility and Responsive Verification

- [x] 9.1 Associate every form label, instruction, description, and error programmatically and expose asynchronous save, upload, reorder, and submission states to assistive technology.
- [x] 9.2 Verify logical headings, focus order, visible focus, keyboard-only completion, minimum target sizing, and non-drag alternatives across the complete author journey.
- [x] 9.3 Verify setup, outline editing, activity authoring, quality checks, preview, and release remain usable at desktop, tablet, and mobile breakpoints.
- [x] 9.4 Add automated accessibility checks where supported and record a manual keyboard and screen-reader verification checklist for behaviors automation cannot prove.

## 10. Templates, Duplication, and Exchange Boundary

- [x] 10.1 Implement internal template discovery and template-based draft creation through the same idempotent aggregate creation contract.
- [x] 10.2 Add template and whole-course duplication tests for regenerated identifiers, source attribution, organization scope, and excluded learner or publication state.
- [x] 10.3 Define import and export adapter interfaces and a validation-report schema that identify every unsupported construct before persistence.
- [x] 10.4 Implement the agreed first-release import or export slice, or explicitly defer format execution while retaining tested adapter boundaries for Common Cartridge and QTI follow-on work.

## 11. Migration and Release Verification

- [x] 11.1 Place canonical Studio navigation behind a feature flag and verify authorized pilot users can complete a realistic course from blank draft through review submission.
- [x] 11.2 Redirect legacy wizard deep links to the corresponding Studio draft while retaining compatibility adapters for the agreed migration window.
- [x] 11.3 Remove the shallow Studio draft form and legacy wizard navigation after usage, data-integrity, and rollback checks pass.
- [x] 11.4 Run focused backend and frontend tests, full relevant suites, production build, OpenSpec validation, and course-authoring browser smoke tests.
- [x] 11.5 Capture performance for representative large course graphs, verify autosave payload and latency bounds, and address regressions before general release.
- [x] 11.6 Document the final role policy, creator workflow, recovery behavior, review and publishing responsibilities, known interoperability limits, and rollback procedure.
