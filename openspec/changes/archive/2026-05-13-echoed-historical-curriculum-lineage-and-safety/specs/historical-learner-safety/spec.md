## MODIFIED Requirements

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
