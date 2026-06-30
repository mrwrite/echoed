# learner-portal-v2 Specification

## ADDED Requirements

### Requirement: Learner Portal SHALL organize access around products
EchoEd SHALL evolve the current student dashboard into Learner Portal V2, where learners see products, learning paths, resources, downloads, progress, and completion artifacts.

#### Scenario: Learner opens portal
- **WHEN** a learner opens the V2 learner portal
- **THEN** EchoEd shows accessible products and the current next learning action

#### Acceptance Criteria
- Existing student course progress remains visible.
- Existing governed lesson start/continue behavior remains intact.
- Existing certificates remain visible.

### Requirement: Learner Portal SHALL support member-style access over time
Learner Portal SHALL support future membership and subscription access without requiring a new learner runtime.

#### Scenario: Learner has access to multiple product types
- **WHEN** a learner has access to a course-backed product, learning path, and downloadable artifact
- **THEN** EchoEd presents them in one learner portal experience

#### Acceptance Criteria
- Access display can be backed by current enrollments first.
- Access grants can replace or augment enrollment lookup in later phases.

## MODIFIED Requirements

### Requirement: Student-facing language SHALL migrate toward learner/member language
Existing student behavior SHALL be preserved while V2 UI language shifts toward learner and member concepts.

#### Scenario: Existing student starts a lesson
- **WHEN** a student uses the V2 learner portal to continue a course
- **THEN** EchoEd uses the same governed course runtime and progress APIs currently used by the student dashboard

#### Acceptance Criteria
- No parallel progress tracking is introduced.
- Existing smoke tests remain valid.

