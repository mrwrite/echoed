# shell-bootstrap-and-navigation-readiness Specification

## Purpose
TBD - created by archiving change echoed-auth-org-session-foundation-hardening. Update Purpose after archive.
## Requirements
### Requirement: Shell rendering waits for resolved authenticated readiness
The platform SHALL withhold role-aware shell rendering until authenticated session, active organization, permissions state, and canonical UX entry state reach a resolved outcome.

#### Scenario: Bootstrap is still resolving
- **WHEN** the authenticated shell loads before session, active organization, permissions state, or canonical entry state is fully resolved
- **THEN** the platform shows a consistent loading or unavailable state instead of rendering sidebar or dashboard content from incomplete context

#### Scenario: Bootstrap resolves successfully
- **WHEN** authenticated bootstrap completes with a usable session and organization context
- **THEN** the shell renders from the resolved session outcome without corrective role or navigation flash

### Requirement: Sidebar and role-aware navigation are deterministic on first paint
The platform SHALL derive sidebar and role-aware navigation from resolved org and permission context only, and SHALL preserve consistent responsive navigation behavior across viewport sizes.

#### Scenario: User lands on the app after login
- **WHEN** the first authenticated shell paint occurs after login bootstrap
- **THEN** sidebar content and visible navigation match the resolved role and active organization on the first stable render

#### Scenario: Permissions change after organization switch
- **WHEN** a confirmed organization switch changes the user's applicable role or permissions
- **THEN** navigation updates from the new resolved context without briefly showing stale items from the prior organization

### Requirement: Dashboard entry is stable after canonical bootstrap
The platform SHALL render dashboard and home entry surfaces only after the canonical bootstrap flow has resolved the user's authenticated destination state and applicable UX state contract.

#### Scenario: User reaches dashboard from login
- **WHEN** a successful login leads to dashboard or home navigation
- **THEN** the destination renders from resolved session, org, onboarding, permission, and UX state rather than from local assumptions that are corrected later

#### Scenario: Organization lookup cannot produce a usable destination
- **WHEN** authenticated bootstrap cannot resolve a usable active organization or destination context
- **THEN** the platform shows a consistent unavailable or redirect outcome instead of silently landing on `/home`

### Requirement: Loading and unavailable states are consistent across shell entry
The platform SHALL use consistent loading, blocked, unavailable, and retry states for unresolved, rejected, or unusable authenticated entry outcomes.

#### Scenario: Authenticated entry is unresolved
- **WHEN** the app is waiting on canonical bootstrap completion
- **THEN** shell-adjacent entry surfaces use a shared loading contract

#### Scenario: Authenticated entry is unusable
- **WHEN** the app resolves an authenticated state that still cannot enter the normal shell because onboarding, active-org, or governed visibility requirements are unmet
- **THEN** the user sees a clear redirect or unavailable-state outcome rather than an ambiguous partial shell

### Requirement: Pilot-critical shell entry and return paths remain visually stable

The platform SHALL keep the authenticated shell, header, sidebar, and primary content region stable across dashboard entry, role-aware navigation, and return-from-lesson transitions.

#### Scenario: Student returns from a lesson
- **WHEN** a student exits a lesson back to the dashboard
- **THEN** the dashboard re-enters through the resolved authenticated shell without broken navigation, contradictory role cues, or displaced primary content

#### Scenario: Teacher reaches the dashboard after login
- **WHEN** a teacher completes authenticated bootstrap
- **THEN** the header, sidebar, and dashboard layout render from resolved role and organization context without flashing stale navigation or partial shell states

