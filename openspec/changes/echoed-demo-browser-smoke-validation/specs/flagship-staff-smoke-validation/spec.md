## ADDED Requirements

### Requirement: Stable flagship teacher walkthrough validation

The system SHALL provide browser smoke coverage for the teacher flagship demo path.

#### Scenario: Teacher validates the flagship staff story
- **WHEN** a seeded demo teacher signs in and opens the dashboard
- **THEN** the teacher dashboard loads successfully
- **AND** the governance summary surface renders
- **AND** the runtime intervention recommendations render
- **AND** the runtime support section renders

### Requirement: Stable flagship admin walkthrough validation

The system SHALL provide browser smoke coverage for the admin flagship demo path.

#### Scenario: Admin validates flagship governance sections
- **WHEN** a seeded demo admin signs in and opens the dashboard
- **THEN** the governance sections render successfully
- **AND** publish readiness renders
- **AND** safe publish validation renders
- **AND** competency evidence integrity renders

### Requirement: Learner and staff auth separation

The browser smoke flow SHALL preserve real learner and staff session separation while validating the flagship demo story.

#### Scenario: Browser smoke switches between learner and staff roles
- **WHEN** the smoke flow signs in as student, teacher, and admin users
- **THEN** each role sees only the surfaces available to that authenticated role
- **AND** the smoke validation does not rely on shared authenticated state across roles
