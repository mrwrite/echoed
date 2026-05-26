## ADDED Requirements

### Requirement: Learner dashboard continuation remains pilot-safe

The platform SHALL present a stable learner dashboard continuation path that helps the student understand the active course, next lesson step, and recovery options when data is unavailable.

#### Scenario: Student lands on the dashboard with an active course
- **WHEN** a learner logs in and has an active governed course path
- **THEN** the dashboard shows the active course and continuation action in a readable, user-friendly way
- **AND** the continuation path does not depend on stale route-local assumptions

#### Scenario: Learner dashboard data cannot be restored
- **WHEN** the student dashboard cannot load continuation data
- **THEN** the learner sees a clear recovery state with retry or alternate navigation instead of a blank or misleading card

### Requirement: Lesson entry and return preserve learner continuity

The platform SHALL let a learner enter the current lesson path and return safely to the dashboard without losing orientation about where to continue next.

#### Scenario: Student enters and exits a lesson
- **WHEN** a learner continues into a lesson and later chooses to return to the dashboard
- **THEN** the platform preserves a coherent continuation path and does not strand the learner in an ambiguous intermediate state
