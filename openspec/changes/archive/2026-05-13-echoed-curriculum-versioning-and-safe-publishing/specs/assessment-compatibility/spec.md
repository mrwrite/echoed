## ADDED Requirements

### Requirement: Curriculum revisions must preserve assessment evidence trust
EchoEd SHALL define assessment compatibility expectations for curriculum revisions without changing the current assessment/mastery architecture.

#### Scenario: Historical assessment evidence remains valid
- **GIVEN** a lesson or course revision affects aligned instructional content
- **WHEN** historical assessment attempts are interpreted
- **THEN** existing attempts and evidence SHALL remain preserved
- **AND** the system SHALL avoid grading corruption or retroactive reassignment of evidence meaning

### Requirement: Compatibility expectations must remain additive
EchoEd SHALL define compatibility rules for aligned lessons and assessments without introducing a second grading or mastery system.

#### Scenario: Assessment architecture remains canonical
- **GIVEN** assessments, attempts, attempt events, and mastery summaries already exist
- **WHEN** revision compatibility rules are applied
- **THEN** those existing structures SHALL remain authoritative
- **AND** compatibility interpretation SHALL be additive rather than a new assessment engine
