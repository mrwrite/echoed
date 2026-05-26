## ADDED Requirements

### Requirement: Assessment taxonomy is canonical and governed
The system SHALL represent assessments through one canonical taxonomy that covers formative, summative, lesson-level, unit-level, course-level, and mastery-check use cases.

#### Scenario: Educator creates a course summative assessment
- **WHEN** an educator defines a summative assessment for a course
- **THEN** the system stores it as the canonical assessment type rather than an ad hoc quiz or lesson-specific special case

#### Scenario: Learner opens a lesson-level assessment
- **WHEN** a learner enters an assessment tied to a lesson
- **THEN** the system resolves it through the same canonical assessment model used for unit and course assessments

### Requirement: Assessment lifecycle and attempt states are authoritative
The system SHALL expose a canonical assessment lifecycle that governs availability, attempt creation, submission, review, grading, feedback release, and expiration.

#### Scenario: Assessment is unavailable to the learner
- **WHEN** the governed assessment lifecycle determines that an assessment is not currently available
- **THEN** the system returns an explicit unavailable assessment state rather than substituting a different assessment

#### Scenario: Learner submits an assessment attempt
- **WHEN** a learner submits an assessment attempt
- **THEN** the system records the attempt against the authoritative lifecycle state and does not treat the submission as a standalone transient UI event

### Requirement: Retake policy and evidence scope are governed
The system SHALL enforce retake policy, evidence retention, and attempt scoping from authoritative assessment policy rather than client-side assumptions.

#### Scenario: Learner exceeds the retake policy
- **WHEN** the learner has exhausted the allowed retake policy for an assessment
- **THEN** the system prevents another attempt and returns the governed retake-unavailable outcome

#### Scenario: Educator permits a retake
- **WHEN** the educator or governing policy allows a retake
- **THEN** the new attempt remains linked to the prior evidence history and does not erase the earlier attempt record
