## ADDED Requirements

### Requirement: Assessment attempts are authoritative evidence records
The system SHALL retain each assessment attempt as an evidence record with submission provenance and attempt history.

#### Scenario: Learner submits an answer set
- **WHEN** a learner submits an assessment response
- **THEN** the system stores the submission as an evidence-bearing attempt record rather than overwriting prior answers

#### Scenario: Institution audits an attempt
- **WHEN** an institution reviews the learner's attempt history
- **THEN** the system can show the original submission lineage and the governed assessment context that produced it

### Requirement: Grading and educator review are auditable
The system SHALL make grading, review, override, and feedback release actions auditable and attributable.

#### Scenario: Educator applies a manual grade
- **WHEN** an educator manually grades an attempt
- **THEN** the system stores the grading event with attribution and preserves the original attempt record

#### Scenario: Educator overrides a prior score
- **WHEN** an educator overrides an existing score or rubric result
- **THEN** the system records the override as a new auditable event instead of deleting the prior grade history

### Requirement: Anti-corruption safeguards protect institutional records
The system SHALL prevent assessment and mastery records from being silently corrupted by client-side assumptions or mutable replacement workflows.

#### Scenario: Client retries a submission request
- **WHEN** a duplicate or retried submission request arrives
- **THEN** the system resolves it through idempotent or governed attempt handling rather than creating contradictory evidence rows

#### Scenario: A record is later re-read for reporting
- **WHEN** the assessment record is loaded for institutional reporting
- **THEN** the system returns the authoritative evidence and grading history without relying on transient UI state
