## MODIFIED Requirements

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
