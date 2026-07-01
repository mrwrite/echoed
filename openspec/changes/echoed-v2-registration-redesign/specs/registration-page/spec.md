## ADDED Requirements

### Requirement: Premium Registration Experience

EchoEd SHALL provide a premium responsive account creation page with two columns, clear form hierarchy, role explanations, organization setup guidance, benefits, and journey preview.

#### Scenario: Visitor opens registration page

- **WHEN** a visitor navigates to `/registration`
- **THEN** the page presents account creation in a polished two-column layout
- **AND** the form fields remain available for first name, last name, email, role, organization setup, password, and confirmation

### Requirement: Registration Behavior Preserved

The registration redesign SHALL preserve existing registration behavior.

#### Scenario: User submits registration

- **WHEN** a user submits the registration form
- **THEN** the existing `onSubmit()` handler is used
- **AND** the existing form controls, validators, organization setup behavior, and backend registration API call remain unchanged
