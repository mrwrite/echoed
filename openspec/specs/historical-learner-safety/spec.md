# historical-learner-safety Specification

## Purpose
TBD - created by archiving change echoed-curriculum-versioning-and-safe-publishing. Update Purpose after archive.
## Requirements
### Requirement: Curriculum revision must preserve historical learner evidence
The system SHALL preserve learner progress, runtime support context, and historically relevant curriculum interpretation as published curriculum evolves. Superseded or successor curriculum revisions SHALL not silently invalidate or reassign `StudentCourse`, `StudentUnitProgress`, or `SegmentProgress` records.

#### Scenario: Learner progress references superseded curriculum
- **WHEN** learner progress points to curriculum that later becomes superseded, deprecated, or archived
- **THEN** the progress records SHALL remain valid against their original curriculum identifiers
- **AND** successor or deprecation context SHALL be additive interpretive metadata rather than destructive reassignment

#### Scenario: Historical learner context is inspected after revision changes
- **WHEN** staff or reporting consumers inspect learner records created under an older curriculum revision
- **THEN** the system SHALL preserve enough historical curriculum context to interpret the learner state accurately
- **AND** governed delivery SHALL remain unchanged for active learner flows unless a separate explicit migration path is introduced later

### Requirement: Archival and deprecation must avoid orphaned learner states
EchoEd SHALL define archival and deprecation safeguards that preserve interpretability of learner records.

#### Scenario: Deprecated curriculum remains historically interpretable
- **GIVEN** previously delivered curriculum is no longer current
- **WHEN** it is deprecated or archived
- **THEN** the system SHALL preserve safe references needed to interpret historical learner states
- **AND** it SHALL avoid destructive removal that would orphan progression or evidence records

