## ADDED Requirements

### Requirement: Superseded curriculum revisions SHALL remain historically interpretable
The system SHALL preserve superseded curriculum revisions as historically interpretable records after newer safe revisions exist. Staff, reporting, and governance consumers SHALL be able to understand that a record has been superseded without losing access to the historical record that learner progress or evidence referenced.

#### Scenario: Older course revision has a current successor
- **WHEN** a course revision is superseded by a newer safe revision
- **THEN** the historical course revision SHALL remain interpretable for staff and reporting use
- **AND** the successor relationship SHALL be visible as read-only context rather than as destructive replacement

### Requirement: Governed learner delivery SHALL continue to prefer current safe revisions
The system SHALL keep learner-facing governed delivery anchored to current safe curriculum where existing availability and progression rules already do so. Historical revision interpretation SHALL not create a learner-facing revision selector or alternate governed progression path.

#### Scenario: Learner accesses governed content after a successor exists
- **WHEN** a successor revision exists for previously published curriculum
- **THEN** governed delivery SHALL continue using the current safe content according to existing delivery rules
- **AND** the existence of superseded content SHALL not create a parallel learner runtime flow
