# staff-lineage-safety-surface-integration Specification

## Purpose
TBD - created by archiving change echoed-staff-lineage-and-safety-visibility. Update Purpose after archive.
## Requirements
### Requirement: Staff governance UI SHALL render lineage and safety status beside existing governance sections
The system SHALL present lineage and historical-safety visibility for authorized staff/admin users within the current governance UI beside publish-readiness and safe-publish sections. The surface SHALL show aggregate status, blocking issues, warnings, and affected entity context without introducing workflow actions.

#### Scenario: Staff inspects lineage and safety context in course governance UI
- **WHEN** an authorized staff or admin user opens a course governance surface with lineage or safety results
- **THEN** the UI SHALL render lineage and safety status beside existing publish-readiness and safe-publish sections
- **AND** the surface SHALL show blocking issues and warnings with affected entity type and title

### Requirement: Staff lineage and safety UI SHALL remain bounded and read-only
The system SHALL keep lineage and safety visibility scoped to read-only operational context. It MUST NOT add publish buttons, rollback controls, grading actions, or destructive workflow affordances as part of this capability.

#### Scenario: Staff views historical assessment or learner-progress risks
- **WHEN** the governance UI shows assessment-evidence or learner-progress safety issues
- **THEN** it SHALL provide read-only warning and blocking context only
- **AND** the surface SHALL not expose publish, rollback, or mutation actions

### Requirement: Learner-facing UI SHALL not expose staff lineage panels
The system SHALL keep learner and student UI surfaces free from staff-only lineage and safety panels unless a separate learner-safe requirement explicitly adds them later.

#### Scenario: Learner opens curriculum or progress UI after staff lineage visibility exists
- **WHEN** a learner or student user navigates learner-facing curriculum or progress surfaces
- **THEN** the UI SHALL not render lineage warning panels, historical safety issue lists, or staff-only governance controls
- **AND** governed learner delivery behavior SHALL remain unchanged

