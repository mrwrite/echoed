## 1. Workflow Governance

- [x] 1.1 Extend curriculum governance contracts for draft, review, approved, and published lifecycle behavior across course, unit, lesson, and aligned assessment content.
- [x] 1.2 Add readiness validation rules for academic completeness, source coverage, learner-safe visibility, and deterministic ordering.
- [x] 1.3 Preserve role-based author, reviewer, approver, and learner visibility boundaries throughout the workflow.

## 2. Publishing and Preview

- [x] 2.1 Implement bounded publish-readiness and staff preview rules for course, unit, and lesson content using existing governance foundations.
- [x] 2.2 Preserve unavailable-state handling for not-yet-published learner content while allowing authorized staff inspection.
- [x] 2.3 Ensure pathway, course, unit, and lesson ordering stays deterministic and governed before publication.

## 3. Versioning and Maintenance

- [ ] 3.1 Add additive curriculum versioning and revision metadata without rewriting the content model.
- [ ] 3.2 Define published edit, draft revision, archival, and deprecation behavior that preserves historical learner safety.
- [ ] 3.3 Verify published maintenance changes do not corrupt learner progress, attempts, mastery evidence, or certifications.

## 4. Assessment Alignment Governance

- [ ] 4.1 Add readiness checks for aligned assessments, learner availability gating, and competency alignment compatibility.
- [ ] 4.2 Preserve historical attempt and evidence integrity when governed curriculum content is revised or republished.
- [ ] 4.3 Keep assessment governance additive to the existing assessment/mastery foundation with no new grading or workflow engine.

## 5. Authoring UX Boundaries and Verification

- [x] 5.1 Add bounded educator/content-admin authoring and review surfaces with readiness indicators, missing-field guidance, and compliance warnings.
- [x] 5.2 Reuse premium UX state primitives for authoring governance loading, empty, error, retry, and publish-readiness states.
- [x] 5.3 Add focused regression coverage for lifecycle behavior, learner-safe visibility, preview behavior, published edit rules, and no learner progression corruption.

## Follow-Ups

- [ ] Add additive curriculum versioning and revision metadata
- [ ] Define published edit, draft revision, archival, and deprecation behavior
- [ ] Add historical learner-progress safeguards for published content edits
- [ ] Add assessment alignment readiness checks
- [ ] Add learner availability gating checks for aligned assessments
- [ ] Preserve historical attempt/evidence integrity across curriculum revisions
- [ ] Add unit-level publish-readiness inspection
- [ ] Add lesson-level publish-readiness inspection
- [ ] Add staff preview flow for unpublished content
- [ ] Add publish/unpublish workflow with strict governance
- [ ] Add route-level staff gating tests for readiness UI
- [ ] Clean up noisy console/error handling in dashboard tests