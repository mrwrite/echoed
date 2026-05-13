# curriculum-versioning-and-maintenance Specification

## Purpose
TBD - created by archiving change echoed-curriculum-authoring-governance. Update Purpose after archive.
## Requirements
### Requirement: Curriculum versioning preserves historical learner safety
The system SHALL support additive versioning, revision, archival, and maintenance semantics for curriculum content while preserving historical learner progress, attempts, mastery evidence, and certification trust.

#### Scenario: Published revisions do not corrupt learner history
- **WHEN** staff creates a revision to published curriculum content
- **THEN** historical learner progress and evidence tied to prior published content MUST remain interpretable and safe

#### Scenario: Material changes are governed separately from draft edits
- **WHEN** staff proposes a material change to published curriculum
- **THEN** the system SHALL require governed revision behavior rather than treating the change like a normal draft edit

#### Scenario: Archived curriculum is not learner-deliverable
- **WHEN** curriculum content is archived or deprecated
- **THEN** new learner delivery MUST NOT use it while historical records remain preserved

