## ADDED Requirements

### Requirement: Registration captures organization setup intent
The system SHALL let a registrant explicitly choose whether to create an organization during first-run setup, collect the minimum organization details needed for that setup path, and explain what will happen after account creation.

#### Scenario: User opts into organization setup during registration
- **WHEN** a registrant enables organization setup and submits a valid registration form
- **THEN** the system records normalized pending organization setup details for post-login onboarding and completes account registration without losing the provided organization information

#### Scenario: User skips organization setup during registration
- **WHEN** a registrant submits a valid registration form without enabling organization setup
- **THEN** the system completes account registration without storing pending organization setup details

### Requirement: First-run routing enforces organization onboarding when required
The system SHALL route authenticated non-super-admin users to organization onboarding until they have an actionable non-personal organization context or have completed the required setup path.

#### Scenario: Pending organization setup exists
- **WHEN** an authenticated user has pending organization setup details from registration
- **THEN** the system routes the user to organization onboarding before allowing normal dashboard navigation

#### Scenario: User has only a personal organization
- **WHEN** an authenticated non-super-admin user has no organizations other than a personal organization
- **THEN** the system routes the user to organization onboarding before allowing normal dashboard navigation

#### Scenario: User already has a non-personal organization
- **WHEN** an authenticated user has at least one non-personal organization available
- **THEN** the system allows the user to continue to the dashboard without first-run onboarding

### Requirement: Organization onboarding completes active organization setup
The system SHALL use the onboarding screen as the completion point for first-run organization creation and SHALL establish the created organization as the active organization for the current session.

#### Scenario: Onboarding loads saved registration intent
- **WHEN** a user arrives at organization onboarding with pending setup details
- **THEN** the system pre-fills the onboarding form with the saved organization name and inferred organization type

#### Scenario: Organization creation succeeds during onboarding
- **WHEN** a user submits valid organization onboarding details and creation succeeds
- **THEN** the system clears pending setup details, refreshes available organizations, switches the session into the created organization, refreshes permissions, and navigates the user to the authenticated app

#### Scenario: Organization creation fails during onboarding
- **WHEN** organization creation fails during first-run onboarding
- **THEN** the system keeps the user on the onboarding screen, preserves their entered values, and displays a clear error message
