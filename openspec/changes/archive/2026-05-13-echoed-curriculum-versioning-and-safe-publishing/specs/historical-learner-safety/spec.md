## ADDED Requirements

### Requirement: Curriculum revision must preserve historical learner evidence
EchoEd SHALL preserve historical learner records when published curriculum evolves.

#### Scenario: Historical learner records remain intact
- **GIVEN** a published course or lesson is revised, deprecated, or superseded
- **WHEN** historical learner activity is queried
- **THEN** learner progress, assessment attempts, mastery evidence, certifications, and runtime support evidence SHALL remain intact
- **AND** those records SHALL not be rewritten to match the newest curriculum revision

### Requirement: Archival and deprecation must avoid orphaned learner states
EchoEd SHALL define archival and deprecation safeguards that preserve interpretability of learner records.

#### Scenario: Deprecated curriculum remains historically interpretable
- **GIVEN** previously delivered curriculum is no longer current
- **WHEN** it is deprecated or archived
- **THEN** the system SHALL preserve safe references needed to interpret historical learner states
- **AND** it SHALL avoid destructive removal that would orphan progression or evidence records
