## MODIFIED Requirements

### Requirement: Educators receive runtime intervention intelligence as read-only guidance
The system SHALL expose runtime intervention intelligence to authorized educators and staff as read-only guidance only, including when that guidance is delivered through a unified course governance summary payload.

#### Scenario: Authorized educator views intervention intelligence
- **WHEN** an authorized educator or staff user accesses a supported runtime support visibility surface
- **THEN** the system SHALL show the learner’s bounded runtime intervention recommendation and its evidence basis as read-only guidance

#### Scenario: Unauthorized learner-facing surfaces do not receive intervention intelligence
- **WHEN** learner-facing or otherwise unauthorized surfaces are rendered
- **THEN** the system SHALL NOT expose educator-only runtime intervention recommendation visibility there unless a separate learner-safe requirement explicitly adds it later

#### Scenario: Unified governance summary includes runtime intervention guidance
- **WHEN** an authorized staff-facing course governance summary is requested
- **THEN** the system SHALL include bounded runtime intervention recommendation context in that summary payload
- **AND** it SHALL remain read-only guidance rather than an automatically executed intervention
