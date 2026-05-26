# assessment-evidence-and-mastery-safety Specification

## Purpose
TBD - created by archiving change echoed-historical-curriculum-lineage-and-safety. Update Purpose after archive.
## Requirements
### Requirement: Historical assessment evidence SHALL remain unambiguous across revisions
The system SHALL preserve `StudentAssessmentAttempt`, `StudentAssessmentAnswer`, and `AssessmentAttemptEvent` records against the assessment revisions they were recorded against. Successor assessment metadata SHALL not rewrite or duplicate historical evidence.

#### Scenario: Assessment revision has attempts before a successor exists
- **WHEN** an assessment with recorded attempts later receives lineage to a successor revision
- **THEN** existing attempts, answers, and attempt events SHALL remain attached to the original assessment revision
- **AND** lineage SHALL be used only to interpret the relationship between revisions

### Requirement: Mastery interpretation SHALL preserve historical evidence meaning
The system SHALL preserve competency alignment and mastery-summary interpretation for historical evidence so revision changes do not create grading ambiguity or contradictory evidence attribution.

#### Scenario: Mastery summary includes evidence from superseded assessments
- **WHEN** mastery reporting reads evidence produced by an assessment revision that has a successor
- **THEN** the system SHALL preserve the original assessment evidence context
- **AND** mastery interpretation SHALL not imply that the evidence was produced by the successor revision unless a later explicit compatibility rule states so

