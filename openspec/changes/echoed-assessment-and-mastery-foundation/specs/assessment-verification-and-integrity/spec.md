## ADDED Requirements

### Requirement: Assessment state and mastery calculations are deterministic
The system SHALL compute assessment state and mastery results through deterministic rules that produce the same outcome for the same authoritative inputs.

#### Scenario: Two consumers evaluate the same attempt
- **WHEN** two consumers read the same authoritative attempt and policy inputs
- **THEN** both consumers observe the same assessment and mastery result

#### Scenario: Assessment policy changes
- **WHEN** the policy for a future attempt changes
- **THEN** prior attempt results remain stable and reproducible from their original evidence and policy context

### Requirement: Learner and educator visibility are consistently enforced
The system SHALL enforce learner, educator, and institutional visibility through the same canonical rules across assessment, mastery, and reporting surfaces.

#### Scenario: Learner requests educator-only grading details
- **WHEN** a learner opens grading details that are not released
- **THEN** the system hides the educator-only information consistently

#### Scenario: Educator requests cohort assessment context
- **WHEN** an educator opens cohort assessment context
- **THEN** the system exposes the educator-visible evidence and mastery data allowed by policy

### Requirement: Reporting and audit outputs remain consistent with stored evidence
The system SHALL ensure reporting and audit outputs are consistent with the authoritative evidence, grading, and mastery records.

#### Scenario: Audit report is regenerated later
- **WHEN** an audit or reporting output is regenerated after the fact
- **THEN** it matches the persisted evidence and grading history for the same assessment scope

#### Scenario: Evidence is reconciled with mastery
- **WHEN** an institution reconciles mastery with stored attempt evidence
- **THEN** the reconciliation uses the same canonical assessment records as reporting and learner delivery
