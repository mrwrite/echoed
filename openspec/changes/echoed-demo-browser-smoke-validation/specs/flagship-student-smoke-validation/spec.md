## ADDED Requirements

### Requirement: Stable flagship student walkthrough validation

The system SHALL provide browser smoke coverage for the flagship student path using deterministic demo credentials and the existing governed learner flow.

#### Scenario: Student walks the flagship course path
- **WHEN** a seeded demo student signs in and opens the dashboard
- **THEN** the dashboard loads successfully
- **AND** the student can start or continue the flagship course
- **AND** the lesson view and progression path render successfully
- **AND** the flagship assessment view loads without breaking the governed learner flow

### Requirement: Production-aligned learner auth behavior

The browser smoke flow SHALL validate learner behavior through the real auth and session path without bypasses.

#### Scenario: Student session is established during smoke validation
- **WHEN** the browser smoke signs in as a seeded demo student
- **THEN** the session is created through the production-aligned login path
- **AND** the smoke flow does not inject fake learner state or bypassed permissions
