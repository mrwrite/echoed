# api-demo-and-test-foundation-hardening Specification

## Purpose
Define consistency requirements for API serialization, UUID handling, error normalization, DTO behavior, governance enforcement, demo reliability, seed reliability, and test coverage hardening.

This specification preserves the current backend route families, analytics foundations, governance foundations, and demo model while extending them through stronger consistency and verification.

## Requirements

### Requirement: API serialization and DTO behavior are consistent
The platform SHALL expose equivalent domain concepts through predictable and compatible response structures across relevant route families.

#### Scenario: Frontend consumes related course or lesson data
- **WHEN** equivalent curriculum or progress concepts are returned by different endpoints
- **THEN** serialization behavior is consistent enough to avoid unnecessary frontend-specific compensating logic

#### Scenario: UUID-bearing payloads are returned across APIs
- **WHEN** identifiers are serialized in request or response flows
- **THEN** UUID handling remains normalized and predictable across the platform

### Requirement: Error responses and governance enforcement are normalized
The platform SHALL provide consistent error semantics and governance enforcement behavior across routes that operate on governed academic data.

#### Scenario: User requests unauthorized or unavailable governed content
- **WHEN** access fails because of role, governance state, or missing readiness
- **THEN** the platform returns a normalized failure shape and preserves canonical governance rules

#### Scenario: Equivalent governance rule is enforced from multiple endpoints
- **WHEN** the same lesson or curriculum restriction is encountered through different routes
- **THEN** the platform applies the same canonical governance decision rather than route-specific variants

### Requirement: Demo and seed environments are institutionally reliable
The platform SHALL support idempotent seeding, dependable demo accounts, reliable demo enrollments, approved-ready demo lessons, and stable demo organization context.

#### Scenario: Demo seed runs more than once
- **WHEN** seed logic is executed repeatedly
- **THEN** the resulting demo environment remains valid and usable without duplicating or corrupting the expected institutional dataset

#### Scenario: Demo user enters the product
- **WHEN** a seeded learner, teacher, or admin account signs in
- **THEN** the account lands in a reliable, role-appropriate, fully usable demo state

### Requirement: Test infrastructure covers core hardening surfaces
The platform SHALL increase backend and frontend verification coverage for auth, onboarding, governance, lesson delivery, seeded environments, and critical UI stability.

#### Scenario: Hardening behavior changes in a fragile domain
- **WHEN** auth, onboarding, shell, lesson, progress, or governance logic changes
- **THEN** automated verification exists to detect regressions in those core flows

#### Scenario: Seeded environment is validated
- **WHEN** demo or seed workflows are used as operational or QA dependencies
- **THEN** automated verification confirms that expected accounts, orgs, enrollments, and learner-facing curriculum states exist
