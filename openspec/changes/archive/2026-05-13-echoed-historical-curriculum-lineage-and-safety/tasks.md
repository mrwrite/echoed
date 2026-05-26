## 1. Lineage Metadata Foundations

- [x] 1.1 Add bounded predecessor and successor metadata support for curriculum and assessment entities with backward-compatible defaults.
- [x] 1.2 Extend schemas and serializers so staff/admin and reporting paths can read lineage metadata without changing learner-safe serialization.
- [x] 1.3 Add focused migration and compatibility tests proving lineage metadata is additive and non-destructive.

## 2. Historical Safety Validation

- [x] 2.1 Extend governance helpers to validate lineage coherence, superseded interpretation, and safe historical publish boundaries.
- [x] 2.2 Add learner-progress and assessment-evidence safety checks that prove historical records remain anchored to original revisions.
- [x] 2.3 Add regression coverage for no-mutation guarantees across progress, attempts, mastery, runtime support evidence, and certifications.

## 3. Reporting and Staff Visibility

- [ ] 3.1 Extend read-only reporting and governance contracts with lineage and historical-safety context for staff/admin users.
- [ ] 3.2 Add bounded staff/admin visibility for successor, superseded, deprecation, and rollback-candidate context without workflow actions.
- [x] 3.3 Verify learner-facing delivery and serialization remain free of staff-only lineage warnings and controls.

## 4. Compatibility and Verification

- [x] 4.1 Add certification and reporting compatibility coverage for historical curriculum titles, metadata, and evidence interpretation.
- [x] 4.2 Verify governed learner delivery remains stable when superseded or deprecated revisions exist.
- [x] 4.3 Document deferred workflow boundaries for publish, republish, rollback, and archival actions so later phases build on these safety guarantees.

## Follow-Ups

- [ ] Extend read-only reporting and governance contracts with lineage and historical-safety context for staff/admin users
- [ ] Add bounded staff/admin visibility for successor, superseded, deprecation, and rollback-candidate context
- [ ] Add successor/predecessor dereferencing and target-existence validation
- [ ] Add same-entity compatibility checks across previous/superseded references
- [ ] Define semantic compatibility rules between old and new assessment revisions
- [ ] Add certification-to-attempt or certification-to-evidence lineage
- [ ] Add persisted mastery-evidence lineage support if mastery evidence becomes first-class
- [ ] Expose lineage/safety validation through bounded staff read-only endpoints
- [ ] Add staff UI for lineage/safety warnings
- [ ] Define bounded rollback behavior without destructive reassignment
- [ ] Clean up repo-wide Pydantic v2 and `datetime.utcnow()` warnings