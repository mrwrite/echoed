## ADDED Requirements

### Requirement: Governance summary composition SHALL use a shared read-only backend boundary
The system SHALL compose the course governance summary through a shared backend read-model layer rather than duplicating aggregation logic across route handlers or dashboard-specific code paths.

#### Scenario: Multiple staff routes need the same governance summary
- **WHEN** more than one authorized staff-facing surface needs course governance summary data
- **THEN** those surfaces SHALL reuse the same shared composition boundary
- **AND** they SHALL not reimplement route-local aggregation logic for the same sections

#### Scenario: Composition logic evolves
- **WHEN** the governance summary composition rules change
- **THEN** the system SHALL update the shared read-model boundary
- **AND** staff-facing routes SHALL inherit the change without diverging section assembly behavior

### Requirement: Shared composition SHALL reuse canonical validators as the source of truth
The system SHALL invoke existing deterministic publish-readiness, safe-publish, lineage-safety, competency-integrity, and runtime-intervention helpers as authoritative sources instead of recomputing those rules inside the summary layer.

#### Scenario: Summary needs section status from existing validators
- **WHEN** the summary layer assembles a course governance section
- **THEN** it SHALL derive that section from the existing canonical validator or read helper for that concern
- **AND** it SHALL not define a second normative rule engine for the same governance domain

#### Scenario: Validator output is empty but valid
- **WHEN** an authoritative validator returns a no-warning or no-blocker result
- **THEN** the composition layer SHALL preserve that deterministic outcome in the summary
- **AND** it SHALL not synthesize extra blockers or warnings through heuristic side logic

### Requirement: Shared composition SHALL define bounded scale behavior
The system SHALL define batching, pagination, and future cacheability expectations for course governance summary reads so staff dashboard usage does not degenerate into avoidable N+1 request growth.

#### Scenario: Staff dashboard loads governance summaries for multiple courses
- **WHEN** a staff-facing surface needs governance data for a bounded set of courses
- **THEN** the shared composition boundary SHALL support bounded batching or equivalent fan-out reduction behavior
- **AND** it SHALL avoid requiring one independent frontend request per governance concern per course

#### Scenario: Future caching is considered
- **WHEN** cache strategy is documented for the governance summary
- **THEN** the design SHALL describe future caching boundaries without requiring complex caching implementation in this change
- **AND** the current behavior SHALL remain deterministic and read-only without precomputed snapshot dependence
