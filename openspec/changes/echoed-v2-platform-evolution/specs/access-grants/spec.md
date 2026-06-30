# access-grants Specification

## ADDED Requirements

### Requirement: AccessGrant SHALL decouple product access from payments
EchoEd SHALL introduce AccessGrant as the explicit record that allows a user, learner, team, organization, or membership to access a product, course, program, artifact, or resource.

#### Scenario: Existing enrollment creates product access
- **WHEN** a learner is enrolled in a course-backed product
- **THEN** EchoEd can represent that access as an access grant while preserving the existing enrollment/progress records

#### Acceptance Criteria
- Access grants do not replace current enrollment in the first migration.
- Access grants can be backfilled from existing enrollments.
- Access grants do not weaken existing auth or role rules.

### Requirement: Access grants SHALL prepare EchoEd for commercialization
AccessGrant SHALL become the foundation for future checkout, memberships, subscriptions, bundles, and enterprise entitlements.

#### Scenario: Product is sold later
- **WHEN** a future checkout succeeds
- **THEN** the checkout system grants access by creating or updating AccessGrant records

#### Acceptance Criteria
- Payment provider state remains separate from auth state.
- Product access can be tested without payment integration.

## MODIFIED Requirements

### Requirement: Existing role permissions SHALL remain authoritative
Access grants SHALL not override workspace administration, authoring, governance, or organization permission checks.

#### Scenario: Learner has product access but no authoring role
- **WHEN** a learner has access to a product
- **THEN** the learner can consume permitted learning content
- **AND** cannot access creator/admin authoring routes without existing role permission

#### Acceptance Criteria
- Role-based route guards remain enforced.
- Backend permission checks remain enforced.

