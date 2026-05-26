## ADDED Requirements

### Requirement: UX state rendering uses one canonical state vocabulary
The platform SHALL use one canonical UX state vocabulary for loading, skeleton, blocked, unavailable, empty, error, retry, and resolved states across authenticated shell, learner delivery, and educator workflows.

#### Scenario: Async content is still resolving
- **WHEN** a shell, learner, or educator surface is waiting for authoritative data
- **THEN** the platform renders a canonical loading or skeleton state rather than route-local placeholder behavior

#### Scenario: Data resolution fails
- **WHEN** an async flow fails after an attempted fetch or transition
- **THEN** the platform renders a canonical error state with retry or recovery affordances appropriate to that surface

### Requirement: Blocked and unavailable states are semantically distinct
The platform SHALL distinguish between unavailable content, governed blocked content, empty states, and transient errors so users are not shown ambiguous fallback experiences.

#### Scenario: Governed content is blocked
- **WHEN** a learner or educator encounters a state that is blocked by governance or readiness rules
- **THEN** the platform renders a governed blocked state rather than a generic error or empty state

#### Scenario: No data exists for the current context
- **WHEN** a resolved view legitimately has no content to show
- **THEN** the platform renders a canonical empty state rather than an unavailable or failed state

### Requirement: Async transitions are consistent across routes
The platform SHALL apply consistent async transition behavior for page entry, reload, retry, and mutation-confirmation paths.

#### Scenario: User triggers a transition that requires async confirmation
- **WHEN** a route or workflow transition depends on an async request
- **THEN** the platform shows consistent pending, success, and failure behavior rather than leaving prior state ambiguously visible

#### Scenario: User retries a failed operation
- **WHEN** a retryable failure occurs
- **THEN** the platform preserves a canonical retry state and does not force the user through a divergent recovery pattern per route
