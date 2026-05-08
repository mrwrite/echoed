## ADDED Requirements

### Requirement: Gradebook foundations derive from canonical assessment records
The system SHALL derive gradebook-ready assessment output from authoritative assessment attempts and grading records.

#### Scenario: Educator views a gradebook foundation
- **WHEN** an educator opens a gradebook-oriented view
- **THEN** the system uses canonical assessment and grading records rather than local UI summaries

#### Scenario: Assessment score changes after review
- **WHEN** an assessment score is updated through an auditable review workflow
- **THEN** the gradebook foundation reflects the authoritative score and preserves the review history

### Requirement: Transcript and institutional reporting are evidence-backed
The system SHALL expose reporting data that can be used as the basis for transcripts, learner evidence history, and institutional audit readiness.

#### Scenario: Institution requests evidence history
- **WHEN** an institution requests a learner evidence history for reporting
- **THEN** the system can reconstruct the report from authoritative attempts, grades, and mastery records

#### Scenario: Reporting is generated for a cohort
- **WHEN** a cohort report is produced
- **THEN** the report is consistent with the same canonical assessment records used for grading and mastery

### Requirement: Academic analytics reconcile mastery, grades, and attempts
The system SHALL make analytics consistent across grades, mastery, pacing, and attempt history.

#### Scenario: Educator compares mastery and grades
- **WHEN** an educator inspects mastery analytics alongside grades
- **THEN** the system presents a coherent view derived from the same assessment evidence

#### Scenario: Academic analytics refresh after new evidence
- **WHEN** a new attempt or grading event is recorded
- **THEN** downstream analytics can be regenerated from the authoritative assessment record without conflicting summaries
