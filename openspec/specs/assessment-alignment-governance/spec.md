# assessment-alignment-governance Specification

## Purpose
TBD - created by archiving change echoed-curriculum-authoring-governance. Update Purpose after archive.
## Requirements
### Requirement: Assessment alignment is governed alongside curriculum publishing
The system SHALL apply readiness, competency-alignment, learner-availability, and evidence-preservation rules to assessments that are aligned with governed curriculum content.

#### Scenario: Unready assessments do not become learner-deliverable
- **WHEN** an aligned assessment lacks required readiness or availability conditions
- **THEN** learners MUST NOT receive it as available assessment content

#### Scenario: Historical attempt evidence remains preserved
- **WHEN** staff revises or republishes curriculum content with aligned assessments
- **THEN** historical attempts and assessment evidence MUST remain preserved and MUST NOT be mutated retroactively

#### Scenario: Competency alignment remains compatible with mastery reporting
- **WHEN** governed assessments are approved and published
- **THEN** required competency alignment metadata SHALL remain compatible with the existing mastery and reporting foundation

