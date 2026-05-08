## ADDED Requirements

### Requirement: Demo seed data includes governed learner-visible instructional paths
The system SHALL seed demo learner environments with deterministic governed instructional paths that include approved-ready learner-visible lessons.

#### Scenario: Demo seed provisions a learner course path
- **WHEN** the demo seed creates its learner-visible course, unit, and lesson data
- **THEN** the seeded learner path includes approved-ready lessons suitable for governed delivery

#### Scenario: Demo learner opens seeded content
- **WHEN** a demo learner enters the seeded lesson flow
- **THEN** the learner receives a deterministic governed lesson sequence rather than an empty or unguided fallback state

### Requirement: Demo delivery reflects production governed behavior
The system SHALL make demo and seeded learner environments exercise the same governed lesson-selection and progression rules used in production learner delivery.

#### Scenario: Demo learner starts a seeded course
- **WHEN** a demo learner triggers course start behavior
- **THEN** progress is created only for the same governed learner-visible lessons that production learner delivery would use

#### Scenario: Governance regression affects demo content
- **WHEN** seeded demo lessons no longer satisfy approved-ready learner delivery requirements
- **THEN** verification fails rather than silently presenting misleading demo behavior
