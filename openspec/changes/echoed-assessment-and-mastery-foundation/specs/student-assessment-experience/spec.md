## ADDED Requirements

### Requirement: Learner assessment delivery is governed and role-aware
The system SHALL deliver assessments to learners only when the assessment is governed, available, and allowed by the learner's authenticated context.

#### Scenario: Learner opens an available assessment
- **WHEN** a learner opens an assessment that is approved for the learner's context
- **THEN** the system delivers the canonical assessment experience rather than a fallback or ungoverned variant

#### Scenario: Learner opens an educator-only assessment
- **WHEN** a learner attempts to access an educator-only assessment
- **THEN** the system returns an explicit unavailable assessment outcome

### Requirement: Assessment unavailable states are explicit and stable
The system SHALL present explicit unavailable states for locked, expired, unpublished, or otherwise disallowed assessments.

#### Scenario: Assessment is expired or locked
- **WHEN** an assessment is expired, locked, or otherwise unavailable
- **THEN** the learner sees a clear unavailable state rather than a blank screen or redirect ambiguity

#### Scenario: Assessment cannot be resolved for the current learner
- **WHEN** the authenticated context cannot resolve a usable assessment
- **THEN** the system does not silently substitute another assessment

### Requirement: Feedback visibility follows attempt and release policy
The system SHALL control feedback visibility based on attempt state, educator release policy, and learner accessibility needs.

#### Scenario: Educator has not released feedback
- **WHEN** feedback is held for educator review
- **THEN** the learner does not see educator-only grading details until the canonical release state allows it

#### Scenario: Learner receives mastery feedback
- **WHEN** feedback is released after grading
- **THEN** the learner sees mastery-oriented feedback that reflects the authoritative attempt outcome
