## ADDED Requirements

### Requirement: Assessment capabilities reuse existing auth, org, session, and progression foundations
The system SHALL build assessment and mastery capabilities on top of the existing auth/org/session authority, governed lesson delivery, and governed progression systems.

#### Scenario: Authenticated educator or learner accesses assessment features
- **WHEN** a user enters assessment features
- **THEN** the system uses the canonical session and organization authority already established elsewhere in EchoEd

#### Scenario: Assessment needs learner progression context
- **WHEN** assessment outcomes influence progression
- **THEN** the system reuses the existing progression authority rather than inventing a parallel progression path

### Requirement: Assessment does not introduce parallel grading or progress engines
The system SHALL avoid creating disconnected assessment, grading, or mastery engines that duplicate existing authority.

#### Scenario: A new assessment service is proposed
- **WHEN** implementation work adds assessment capability
- **THEN** it integrates with the existing progress and lesson-session systems instead of replacing them

#### Scenario: Educator grading and learner progress both need the same evidence
- **WHEN** both grading and progression need the same attempt
- **THEN** they resolve against one authoritative assessment record rather than separate copies

### Requirement: Assessment state changes remain deterministic and auditable
The system SHALL make assessment and mastery state transitions deterministic, reviewable, and consistent across all consumers.

#### Scenario: Assessment state changes from available to submitted
- **WHEN** an assessment state changes
- **THEN** the transition is recorded in a deterministic order that can be audited later

#### Scenario: Reporting and delivery read the same assessment state
- **WHEN** the learner view and reporting view read assessment status
- **THEN** they observe the same authoritative state rather than independently inferred summaries
