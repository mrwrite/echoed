## ADDED Requirements

### Requirement: Public registration cannot assign privileged authority
The backend SHALL assign a safe default global role and personal-organization membership through trusted server logic, regardless of client-supplied role or authority fields.

#### Scenario: Registration requests an administrative role
- **WHEN** an anonymous registration request supplies `admin`, `super_admin`, or another non-default role
- **THEN** the created account receives only the safe default global role and the documented personal-organization membership

### Requirement: Inactive organization memberships cannot establish authority
The platform SHALL require an active membership for organization switching and organization-scoped authorization, including any platform-administrator organization access path.

#### Scenario: User selects an inactive membership
- **WHEN** an authenticated user attempts to switch to or authorize through an inactive organization membership
- **THEN** the backend conceals or denies the organization and preserves the prior session context
