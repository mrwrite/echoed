## MODIFIED Requirements

### Requirement: Curriculum revisions must preserve assessment evidence trust
The system SHALL preserve assessment, answer, attempt-event, competency, and mastery interpretation across revision changes. Assessment compatibility rules SHALL prevent grading ambiguity by keeping historical evidence anchored to the original assessment revision while allowing additive successor context for staff and reporting use.

#### Scenario: Historical assessment evidence is read after successor assessment exists
- **WHEN** reporting or mastery logic reads attempts and evidence from an assessment revision that now has a successor
- **THEN** the historical evidence SHALL remain attached to the original assessment revision
- **AND** successor context SHALL not imply a retroactive grading or evidence reassignment

#### Scenario: Safe-publish validation inspects assessment lineage risk
- **WHEN** governance logic evaluates whether curriculum with revised assessments is safe to publish or republish
- **THEN** it SHALL account for historical evidence preservation risk
- **AND** it SHALL surface warnings or blocking issues without mutating attempts, mastery, or certification records
