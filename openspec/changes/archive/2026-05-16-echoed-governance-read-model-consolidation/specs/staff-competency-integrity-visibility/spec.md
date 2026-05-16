## MODIFIED Requirements

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
