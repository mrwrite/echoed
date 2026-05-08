## ADDED Requirements

### Requirement: Educators can assign and inspect assessments by cohort and scope
The system SHALL allow educators to assign assessments and inspect assigned assessment visibility by cohort, section, lesson, unit, or course scope.

#### Scenario: Educator assigns a cohort assessment
- **WHEN** an educator assigns an assessment to a cohort or section
- **THEN** the system records the assignment against the canonical assessment scope and makes it visible to the intended educator audience

#### Scenario: Educator inspects scoped assessments
- **WHEN** an educator views a unit or course assessment list
- **THEN** the system shows the assessments relevant to that instructional scope

### Requirement: Educators can manually grade with rubrics and review queues
The system SHALL support manual grading, rubric-driven evaluation, and queued review workflows for educator assessment operations.

#### Scenario: Educator grades a submitted attempt
- **WHEN** an educator opens a submitted attempt for review
- **THEN** the system allows rubric-based grading and records the manual grading event as part of the attempt history

#### Scenario: Assessment requires review before release
- **WHEN** an assessment is configured for review before feedback release
- **THEN** the system keeps the attempt in a reviewable state until the educator completes the workflow

### Requirement: Educators can surface intervention and pacing signals
The system SHALL expose mastery, pacing, and intervention signals that help educators identify learners needing support.

#### Scenario: Learner falls behind mastery expectations
- **WHEN** a learner repeatedly misses mastery thresholds
- **THEN** the system exposes an intervention signal to the educator

#### Scenario: Educator reviews cohort pacing
- **WHEN** an educator inspects a cohort assessment overview
- **THEN** the system presents pacing and mastery insight that can inform instructional intervention
