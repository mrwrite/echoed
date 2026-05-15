## 1. Backend Staff Lineage/Safety Contract

- [x] 1.1 Add a staff-only read-only backend contract that aggregates course lineage coherence, learner-progress safety, assessment-evidence safety, and aggregate safety status.
- [x] 1.2 Enforce existing staff/admin/content authorization boundaries and return learner-safe denial behavior for unauthorized or learner-facing access.
- [x] 1.3 Ensure the contract returns structured blocking issues and warnings with affected entity type, identifier, title, and relevant safety context without mutating underlying records.

## 2. Staff Governance UI Integration

- [x] 2.1 Add bounded staff-facing lineage/safety visibility beside existing publish-readiness and safe-publish sections in the current governance UI.
- [x] 2.2 Render aggregate lineage/safety state, blocking issues, warnings, assessment-evidence risks, and learner-progress risks using existing premium UX state primitives.
- [x] 2.3 Keep the UI read-only and omit publish, rollback, grading, or mutation controls.

## 3. Learner-Safe Separation

- [x] 3.1 Verify learner/student views do not receive staff lineage warnings, safety issue lists, or historical governance controls.
- [x] 3.2 Verify governed learner delivery behavior remains unchanged when staff lineage/safety visibility is introduced.

## 4. Regression Verification

- [x] 4.1 Add focused backend tests for staff access, learner denial, lineage coherence issues, learner-progress safety issues, assessment-evidence safety issues, and read-only guarantees.
- [x] 4.2 Add focused frontend or integration tests for staff UI rendering of lineage/safety results and learner non-exposure.
- [x] 4.3 Verify reporting, certification, assessment scoring, and governed delivery behavior remain unchanged after staff lineage/safety visibility is added.

## Follow-Ups

- [ ] Group lineage/safety issues by validator category
- [ ] Add frontend normalization for duplicate or overlapping safety warnings
- [ ] Add route-guard or integration-level staff/learner visibility coverage
- [ ] Add backend regression coverage for governed delivery/certification compatibility alongside the UI surface
- [ ] Add unit/lesson-level lineage safety drill-down