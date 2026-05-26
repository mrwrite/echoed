## ADDED Requirements

### Requirement: Teacher dashboard exposes stable pilot-baseline visibility

The platform SHALL provide a stable teacher dashboard baseline that exposes enough course, learner-progress, and runtime-support state for a pilot walkthrough even when some educator datasets are empty.

#### Scenario: Teacher opens the dashboard with available course context
- **WHEN** an educator reaches the teacher dashboard in a pilot environment
- **THEN** the dashboard exposes a readable course-management and learner-visibility baseline that supports live narration of platform value

#### Scenario: Teacher opens the dashboard with sparse data
- **WHEN** one or more educator sections resolve with no data yet
- **THEN** the dashboard shows intentional empty states rather than collapsed, broken, or misleading panels

### Requirement: Teacher dashboard recovery states remain usable

The platform SHALL provide actionable loading and retry behavior for teacher-facing dashboard sections that depend on asynchronous operational data.

#### Scenario: Educator section fails to load
- **WHEN** a teacher dashboard section cannot load its operational data
- **THEN** the educator sees a clear section-level recovery state with bounded retry behavior instead of losing the whole dashboard context
