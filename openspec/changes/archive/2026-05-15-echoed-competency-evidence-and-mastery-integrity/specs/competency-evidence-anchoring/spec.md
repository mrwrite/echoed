## ADDED Requirements

### Requirement: Competency-backed mastery SHALL remain traceable to authoritative evidence
The system SHALL preserve a traceable relationship between mastery interpretation, `StudentAssessmentAttempt`, `StudentAssessmentAnswer`, `AssessmentAttemptEvent`, and the competency alignment context that was valid when the evidence was produced.

#### Scenario: Staff traces mastery evidence for a learner
- **WHEN** a staff, reporting, or validation consumer inspects a mastery summary
- **THEN** the system SHALL be able to identify the assessment attempt and competency context that produced the interpretation
- **AND** it SHALL not require guessing based on the latest assessment revision alone

#### Scenario: Historical competency alignment is re-read after curriculum evolves
- **WHEN** a historical assessment attempt is read after later curriculum or alignment changes exist
- **THEN** the original evidence context SHALL remain available for interpretation
- **AND** the system SHALL not silently substitute newer competency alignments for the historical record

### Requirement: Historical evidence SHALL remain anchored to its original assessment revision
The system SHALL keep historical attempts, answers, and attempt events attached to the assessment revision that originally produced them, even when successor or superseding revisions later exist.

#### Scenario: Successor assessment exists for a historically attempted assessment
- **WHEN** a historical attempt is read after the assessment has a successor revision
- **THEN** the evidence SHALL remain anchored to the original assessment revision
- **AND** successor metadata SHALL only provide interpretive context rather than reassignment
