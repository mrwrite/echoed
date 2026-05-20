## ADDED Requirements

### Requirement: Bounded demo operational confidence checks

The system SHALL provide lightweight operational checks that give confidence the seeded flagship demo is ready without becoming a full end-to-end suite.

#### Scenario: Operator performs a pre-demo smoke check
- **WHEN** the demo smoke flow is run as part of demo preparation
- **THEN** it validates seeded login readiness, flagship course discoverability, and core student and staff walkthrough surfaces
- **AND** it avoids exhaustive product coverage outside the flagship demo scope

### Requirement: Explicit non-goal boundaries

The smoke validation layer SHALL remain intentionally limited to demo-confidence and regression-validation concerns.

#### Scenario: Smoke coverage scope is reviewed
- **WHEN** new smoke coverage is proposed for this capability
- **THEN** it excludes visual regression tooling, screenshot infrastructure, performance benchmarking, load testing, backend mutation orchestration, and CI redesign
- **AND** it remains maintainable as a lightweight demo-readiness layer
