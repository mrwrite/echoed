## ADDED Requirements

### Requirement: Course drafts follow an explicit governed lifecycle
The platform SHALL represent durable course drafts, review submission, review decisions, version identity, and publication as explicit lifecycle transitions over the canonical curriculum and governance systems.

#### Scenario: Author saves incomplete work
- **WHEN** an authorized author saves a course that is not ready for review or publication
- **THEN** the course remains a durable draft and is not exposed to learners

#### Scenario: Author submits for review
- **WHEN** an authorized author submits a draft that satisfies submission requirements
- **THEN** the platform records the submitted version, author, timestamp, readiness evidence, and review state without publishing it

#### Scenario: Reviewer returns a course
- **WHEN** an authorized reviewer requests changes with feedback
- **THEN** the platform records the decision and feedback, returns the course to an editable governed state, and preserves the submitted version history

#### Scenario: Authorized publisher publishes an approved version
- **WHEN** an authorized publisher selects an approved version that passes canonical safe-publish validation
- **THEN** the platform publishes that immutable version, records the actor and timestamp, and makes only the governed learner-safe projection available

### Requirement: Publish readiness is actionable from the course studio
The platform SHALL expose canonical publish-readiness and safe-publish findings within the course studio with severity, affected entity, and corrective context while preserving governance services as the source of truth.

#### Scenario: Readiness check finds a blocking issue
- **WHEN** the canonical readiness evaluation identifies a blocking course, unit, lesson, activity, assessment, source, or ordering issue
- **THEN** the studio identifies the affected entity and prevents governed publication while allowing the draft to remain editable

#### Scenario: Readiness check passes
- **WHEN** canonical automated readiness and safe-publish checks pass
- **THEN** the platform enables only the next lifecycle actions allowed by the user's capability and does not bypass required human review

### Requirement: Published learner access remains isolated from draft edits
The platform SHALL keep the currently published immutable version learner-visible while authors prepare later drafts or revisions.

#### Scenario: Author edits a published course
- **WHEN** an authorized author begins changing a published course
- **THEN** the system creates or opens a new draft version and preserves the currently published learner experience until a later version is approved and published

#### Scenario: New version replaces published version
- **WHEN** an authorized publisher releases a later approved version
- **THEN** new learner delivery resolves to the new published version while historical version and audit records remain available to authorized staff

