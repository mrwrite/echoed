# deterministic-demo-foundation Specification

## Purpose
TBD - created by archiving change echoed-demo-readiness-and-flagship-experience. Update Purpose after archive.
## Requirements
### Requirement: Canonical demo environment

The system SHALL provide one canonical demo environment composed of a stable demo organization, demo users, and flagship course content.

#### Scenario: Demo seed creates canonical entities

- **WHEN** the demo seed or setup path runs
- **THEN** the canonical demo organization exists
- **AND** the canonical demo admin, teacher, and student accounts exist
- **AND** the flagship "Introduction to Africa" course exists
- **AND** its expected seeded unit and lesson structure exists

### Requirement: Deterministic reseed behavior

The system SHALL support deterministic reseed behavior for demo-scoped entities, including canonical demo users whose identity and credentials must reset to known defaults on repeat runs.

#### Scenario: Demo seed is rerun

- **WHEN** the demo seed runs more than once
- **THEN** canonical demo entities are recreated or refreshed into the same bounded state
- **AND** duplicate demo organizations, users, or flagship course copies are not left behind
- **AND** demo credentials and role memberships remain valid

#### Scenario: Existing demo user rows already exist

- **WHEN** the demo seed encounters an existing canonical demo user
- **THEN** it matches that user by username first and then by email if needed
- **AND** it resets the canonical firstname, lastname, username, email, role, and password fields to the demo defaults

#### Scenario: Duplicate demo user rows exist

- **WHEN** duplicate rows exist for canonical demo usernames or emails
- **THEN** the seed removes stale duplicates before upserting the final canonical demo users
- **AND** the resulting seeded state contains one surviving row per intended demo profile

### Requirement: Stable learner relationships

The system SHALL seed stable section, enrollment, and learner-course relationships for the canonical demo environment.

#### Scenario: Demo participants are seeded

- **WHEN** the demo seed completes
- **THEN** demo learners are enrolled in the flagship course
- **AND** the teacher and admin demo flows can discover those learners through existing platform relationships

