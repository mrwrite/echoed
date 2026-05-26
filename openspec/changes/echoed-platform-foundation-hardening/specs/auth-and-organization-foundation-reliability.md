# auth-and-organization-foundation-reliability Specification

## Purpose
Define the reliability requirements for authentication, session bootstrap, organization context, onboarding gating, and organization switching so EchoEd behaves deterministically across login, first load, onboarding, and role-aware entry flows.

This specification preserves the current auth, organization, and onboarding foundations and extends them through consistency and centralization rather than replacement.

## Requirements

### Requirement: Post-auth session bootstrap is deterministic
The platform SHALL establish user, token, organization, and permissions context through a predictable post-auth bootstrap sequence.

#### Scenario: User logs in successfully
- **WHEN** a user authenticates
- **THEN** the platform resolves authenticated session state, available organizations, active organization context, and initial role-aware routing in a consistent order

#### Scenario: User refreshes an authenticated page
- **WHEN** a user loads a protected route from an existing session
- **THEN** the platform rehydrates auth and organization context without ambiguous intermediate states that change the eventual destination

### Requirement: Onboarding-required evaluation is centralized
The platform SHALL use one canonical decision path for whether onboarding is required.

#### Scenario: Newly registered user requires organization setup
- **WHEN** a non-super-admin user has pending organization setup or lacks a usable institutional context
- **THEN** the platform resolves onboarding-required status through a shared rule rather than conflicting route-local checks

#### Scenario: User already has valid organization context
- **WHEN** a user has an acceptable active organization state for normal app use
- **THEN** the platform does not redirect the user into onboarding due to duplicated or inconsistent gate logic

### Requirement: Personal and institutional organization handling is consistent
The platform SHALL handle personal org and institutional org contexts consistently across auth, onboarding, switching, and dashboard entry.

#### Scenario: User only has a personal organization
- **WHEN** a user has no non-personal organization available
- **THEN** the platform applies the same onboarding and routing interpretation everywhere that org context is evaluated

#### Scenario: User belongs to both personal and institutional orgs
- **WHEN** the user enters or switches context
- **THEN** the platform resolves active organization behavior consistently without silently drifting between org types

### Requirement: Active organization switching is reliable
The platform SHALL maintain active organization consistency across manual switching, login bootstrap, and onboarding completion.

#### Scenario: User switches organizations
- **WHEN** a user intentionally changes active organization
- **THEN** permissions, visible navigation, and route-relevant data refresh against the new canonical org context

#### Scenario: Onboarding creates a new organization
- **WHEN** organization creation completes during onboarding
- **THEN** the created organization becomes the active context through the same canonical switching behavior used elsewhere
