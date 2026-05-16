# Deterministic Demo Foundation

## Purpose

Define a reproducible EchoEd demo environment with stable organization, users, flagship content, and seeded learner relationships so live demos do not depend on manual setup.

## ADDED Requirements

### Requirement: Canonical demo environment

The system SHALL provide one canonical demo environment composed of a stable demo organization, demo users, and flagship course content.

#### Scenario: Demo seed creates canonical entities

- **WHEN** the demo seed or setup path runs
- **THEN** the canonical demo organization exists
- **AND** the canonical demo admin, teacher, and student accounts exist
- **AND** the flagship "Introduction to Africa" course exists
- **AND** its expected seeded unit and lesson structure exists

### Requirement: Deterministic reseed behavior

The system SHALL support deterministic reseed behavior for demo-scoped entities.

#### Scenario: Demo seed is rerun

- **WHEN** the demo seed runs more than once
- **THEN** canonical demo entities are recreated or refreshed into the same bounded state
- **AND** duplicate demo organizations, users, or flagship course copies are not left behind
- **AND** demo credentials and role memberships remain valid

### Requirement: Stable learner relationships

The system SHALL seed stable section, enrollment, and learner-course relationships for the canonical demo environment.

#### Scenario: Demo participants are seeded

- **WHEN** the demo seed completes
- **THEN** demo learners are enrolled in the flagship course
- **AND** the teacher and admin demo flows can discover those learners through existing platform relationships
