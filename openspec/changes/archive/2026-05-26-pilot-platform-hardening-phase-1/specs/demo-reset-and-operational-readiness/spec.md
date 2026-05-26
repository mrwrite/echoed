## ADDED Requirements

### Requirement: Demo preparation documents bounded pilot verification

The system SHALL provide a documented, bounded verification path for preparing and checking the pilot demo environment after a reset or reseed.

#### Scenario: Operator prepares the pilot demo
- **WHEN** a demo operator follows the documented reset and validation steps
- **THEN** the operator can reseed the environment, verify the canonical student path, and confirm the bounded teacher walkthrough expectations without undocumented repair work

### Requirement: Demo runbooks stay aligned with real platform behavior

The system SHALL keep demo reset, smoke validation, and manual verification docs aligned with the current authenticated student and teacher experience.

#### Scenario: Platform behavior changes in a pilot-critical flow
- **WHEN** dashboard, lesson runtime, seed, or smoke behavior changes in a way that affects the pilot walkthrough
- **THEN** the corresponding demo runbooks are updated so operators do not follow stale instructions
