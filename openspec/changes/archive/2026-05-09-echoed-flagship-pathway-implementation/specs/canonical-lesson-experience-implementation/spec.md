## ADDED Requirements

### Requirement: Canonical lesson experience implementation
The system SHALL implement the canonical flagship lesson experience using the instructional flow of activation, story/media/context, guided instruction, exploration/activity, reflection/discussion, assessment/check-for-understanding, mastery signal, remediation, enrichment, and closure.

#### Scenario: Flagship lessons follow the canonical instructional rhythm
- **WHEN** a learner enters a flagship lesson
- **THEN** the lesson MUST present the canonical instructional flow without changing governed delivery or unavailable-state behavior

### Requirement: Lesson behavior preserves institutional runtime semantics
The flagship lesson experience SHALL preserve governed delivery semantics, unavailable-state semantics, accessibility foundations, and existing assessment integration behavior.

#### Scenario: UX polish does not alter runtime authority
- **WHEN** the canonical lesson experience is implemented
- **THEN** it MUST refine presentation and interaction quality without changing backend progression, route, or assessment semantics
