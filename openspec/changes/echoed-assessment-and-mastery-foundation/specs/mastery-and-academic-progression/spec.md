## ADDED Requirements

### Requirement: Mastery thresholds are explicit and scoped to objectives
The system SHALL define mastery thresholds against standards, competencies, or objectives rather than as opaque global flags.

#### Scenario: Course defines objective-based mastery
- **WHEN** a course associates mastery with specific objectives or competencies
- **THEN** the system stores the threshold in a way that can be evaluated per objective rather than as a single course-wide boolean

#### Scenario: Educator reviews mastery rules
- **WHEN** an educator inspects mastery configuration
- **THEN** the system exposes the threshold source and scope used for the mastery decision

### Requirement: Mastery aggregates deterministically across lesson, unit, and course levels
The system SHALL derive unit and course mastery from governed lesson-level evidence using deterministic aggregation rules.

#### Scenario: Learner masters a lesson but not the unit threshold
- **WHEN** lesson evidence reaches mastery but the unit threshold is not yet met
- **THEN** the unit remains not mastered until the aggregated rule is satisfied

#### Scenario: Learner completes all required lesson evidence
- **WHEN** the required lesson-level evidence reaches the configured threshold
- **THEN** the system aggregates that evidence upward into unit and course mastery according to the canonical rule set

### Requirement: Progression eligibility respects mastery and intervention state
The system SHALL use mastery status, remediation state, and educator intervention status to determine whether progression is eligible.

#### Scenario: Learner needs remediation
- **WHEN** mastery thresholds are not met and remediation is required
- **THEN** the system marks the learner as not yet eligible for progression and exposes the intervention state

#### Scenario: Learner satisfies mastery after remediation
- **WHEN** remediation evidence later satisfies the mastery threshold
- **THEN** the learner becomes eligible for the next progression step through the canonical progression authority
