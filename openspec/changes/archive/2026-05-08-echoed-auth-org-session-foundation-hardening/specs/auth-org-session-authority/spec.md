## ADDED Requirements

### Requirement: Active organization resolution is canonical and deterministic
The platform SHALL resolve authenticated active organization from canonical rules and backend-confirmed context rather than frontend array ordering or local guesswork.

#### Scenario: User has multiple organizations
- **WHEN** an authenticated user has more than one available organization
- **THEN** the platform resolves the active organization through a deterministic rule and does not assume `organizations[0]` is authoritative

#### Scenario: User has personal and institutional organizations
- **WHEN** an authenticated user has both personal and institutional organization memberships
- **THEN** the platform applies one canonical interpretation of which organization context is active and whether onboarding is still required

### Requirement: Organization switching is confirmed by the server before session state updates
The platform SHALL update active organization, role context, and dependent permission state only from a server-confirmed organization-switch response.

#### Scenario: User switches organizations successfully
- **WHEN** a user initiates an organization switch and the server confirms the new active organization
- **THEN** the frontend updates session and permission state from the confirmed response rather than from optimistic local state

#### Scenario: Organization switch fails
- **WHEN** a user initiates an organization switch and the server rejects or cannot resolve the target organization
- **THEN** the current active organization state remains unchanged and the platform exposes an explicit failure outcome

### Requirement: Session bootstrap follows one canonical frontend flow
The platform SHALL resolve authenticated session, active organization, onboarding-required status, and permissions through one canonical frontend bootstrap path.

#### Scenario: User lands on a protected route with an existing session
- **WHEN** an authenticated user loads or refreshes a protected route
- **THEN** guards, home entry, dashboard entry, and shell rendering consume the same bootstrap flow and produce one consistent session outcome

#### Scenario: Duplicate bootstrap entry points exist in the app
- **WHEN** the platform resolves authenticated entry
- **THEN** no route-local path bypasses the canonical bootstrap flow to independently hydrate user, org, or permissions state

### Requirement: Onboarding-required evaluation is centralized
The platform SHALL determine onboarding-required status from one shared rule across login, guarded navigation, refresh, and post-bootstrap routing.

#### Scenario: User has no usable institutional organization
- **WHEN** a non-super-admin user has no organizations, only a personal organization, or pending organization setup
- **THEN** the platform consistently resolves onboarding-required status and routes the user to onboarding rather than silently falling through to `/home`

#### Scenario: User has a valid active organization
- **WHEN** a user has an available active organization that satisfies normal app access
- **THEN** the platform does not redirect the user into onboarding because of duplicated or conflicting route-local checks

### Requirement: Auth token handling and login responses are normalized
The platform SHALL treat token attachment, invalid-token handling, and login response parsing through a consistent auth contract.

#### Scenario: Authorized API request is made through a path covered by interceptors
- **WHEN** frontend code issues an authenticated request in a path where auth interceptors already apply
- **THEN** application code does not manually construct a duplicate authorization header

#### Scenario: Token is invalid or expired during bootstrap
- **WHEN** the platform encounters an invalid or expired token while establishing authenticated state
- **THEN** it resolves that failure through the canonical auth flow and does not leave the shell or route state in a partially authenticated condition
