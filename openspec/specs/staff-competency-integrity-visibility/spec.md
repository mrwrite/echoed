# staff-competency-integrity-visibility Specification

## Purpose
TBD - created by archiving change echoed-competency-evidence-and-mastery-integrity. Update Purpose after archive.
## Requirements
### Requirement: Staff and admin users SHALL have read-only competency-evidence integrity visibility
The system SHALL expose bounded competency-evidence integrity, mastery-ambiguity, and assessment-compatibility warnings to authorized staff/admin users through read-only backend contracts, governance summary payloads, or governance surfaces.

#### Scenario: Staff reviews a course with mastery-integrity risk
- **WHEN** an authorized staff or admin user inspects governance information for a course with ambiguous mastery evidence
- **THEN** the system SHALL show integrity warnings with affected entity type, title, and compatibility context
- **AND** the surface SHALL remain read-only

#### Scenario: Educator reviews assessment compatibility context
- **WHEN** an educator-facing visibility surface includes mastery-integrity results
- **THEN** the system SHALL explain the assessment compatibility or historical-evidence risk in bounded terms
- **AND** it SHALL not expose reassignment or override actions by default

#### Scenario: Unified governance summary carries competency-integrity context
- **WHEN** an authorized staff-facing course governance summary is requested
- **THEN** the system SHALL include competency-integrity and mastery-risk section data within that summary payload
- **AND** it SHALL preserve the existing bounded integrity semantics rather than redefining them in the aggregation layer

### Requirement: Learner-facing views SHALL not expose staff competency-integrity warnings
The system SHALL keep learner and student surfaces free from staff-only competency-evidence integrity warnings, mastery-risk issue lists, and compatibility governance controls.

#### Scenario: Learner opens governed progress or assessment views
- **WHEN** a learner or student user reads course, progress, mastery, or assessment UI
- **THEN** staff-only competency-integrity warnings SHALL not be rendered
- **AND** learner delivery behavior SHALL remain unchanged

