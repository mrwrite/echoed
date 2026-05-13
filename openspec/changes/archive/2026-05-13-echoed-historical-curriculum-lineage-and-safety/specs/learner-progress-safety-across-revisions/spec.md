## ADDED Requirements

### Requirement: Historical learner progress SHALL remain anchored to original curriculum records
The system SHALL preserve `StudentCourse`, `StudentUnitProgress`, and `SegmentProgress` references against the curriculum records they were originally created for. Successor or supersession metadata SHALL not silently reassign historical learner progress to newer curriculum revisions.

#### Scenario: Lesson revision is superseded after learner progress exists
- **WHEN** learner progress already references a lesson or unit that later gains a successor revision
- **THEN** the historical progress records SHALL remain attached to the original lesson or unit identifiers
- **AND** the successor relationship SHALL be available only as read-only interpretive context

### Requirement: Historical progress SHALL remain valid for reporting and continuity
The system SHALL treat historical progress tied to older revisions as valid institutional evidence even after newer revisions exist, unless an explicit later workflow defines a separate governed migration path.

#### Scenario: Reporting reads progress across superseded curriculum
- **WHEN** staff or reporting logic reads learner progress associated with superseded curriculum
- **THEN** the system SHALL preserve the historical curriculum context needed to interpret that progress
- **AND** the reporting path SHALL not require destructive reassignment to a successor revision
