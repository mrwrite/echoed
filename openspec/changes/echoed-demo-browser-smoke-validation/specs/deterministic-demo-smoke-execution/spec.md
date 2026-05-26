## ADDED Requirements

### Requirement: Deterministic demo smoke execution

The system SHALL provide a bounded browser smoke flow that can run against the seeded EchoEd demo environment without backend-specific test orchestration.

#### Scenario: Smoke flow runs against the seeded demo environment
- **WHEN** an operator runs the demo browser smoke flow after preparing the seeded demo environment
- **THEN** the smoke flow authenticates through the real browser login path
- **AND** it verifies the seeded demo organization and flagship "Introduction to Africa" course are discoverable
- **AND** it completes within a demo-safe bounded execution window

### Requirement: Bounded retry and failure output

The smoke flow SHALL use bounded retry behavior only where needed and SHALL emit clear operator-readable failures.

#### Scenario: A smoke validation step fails
- **WHEN** a role-specific smoke step cannot complete successfully
- **THEN** the output identifies the role, screen, and missing expected condition
- **AND** retries remain limited to known stabilization points
- **AND** the smoke flow does not mask persistent product failures through unbounded waiting
