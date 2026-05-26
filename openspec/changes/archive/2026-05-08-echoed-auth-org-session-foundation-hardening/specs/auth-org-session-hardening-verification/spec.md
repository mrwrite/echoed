## ADDED Requirements

### Requirement: Login bootstrap behavior is regression-tested
The platform SHALL have automated regression coverage for canonical login bootstrap outcomes.

#### Scenario: Login resolves authenticated shell readiness
- **WHEN** login succeeds for a user with a valid active organization and usable permissions
- **THEN** automated tests verify the canonical bootstrap path resolves the correct destination and ready shell state

#### Scenario: Login resolves onboarding-required status
- **WHEN** login succeeds for a user without a usable institutional organization context
- **THEN** automated tests verify the canonical flow routes the user into onboarding instead of the normal shell

### Requirement: Active-organization selection and switching are regression-tested
The platform SHALL have automated coverage for deterministic active-org selection and server-confirmed org switching.

#### Scenario: User has multiple org memberships
- **WHEN** authenticated bootstrap resolves active organization for a user with multiple memberships
- **THEN** automated tests verify the canonical selection behavior and role reconciliation outcome

#### Scenario: User switches organizations
- **WHEN** a confirmed org switch succeeds or fails
- **THEN** automated tests verify frontend state updates only from confirmed server responses and preserves prior state on failure

### Requirement: Permission hydration and shell readiness are regression-tested
The platform SHALL have automated coverage for permission bootstrap and first authenticated paint readiness.

#### Scenario: Permissions are required for sidebar and dashboard rendering
- **WHEN** the shell becomes ready after canonical bootstrap
- **THEN** automated tests verify role-aware navigation and dashboard content do not render from unresolved permission state

#### Scenario: Protected-route refresh occurs with an existing session
- **WHEN** the user refreshes a protected route with a valid persisted session
- **THEN** automated tests verify the canonical bootstrap flow produces one consistent loading and ready-state transition
