## ADDED Requirements

### Requirement: Curriculum authoring follows a governed lifecycle
The system SHALL support a governed curriculum lifecycle for draft, review, approved, and published content across course, unit, lesson, and aligned assessment authoring surfaces.

#### Scenario: Draft content remains staff-only
- **WHEN** a course, unit, lesson, or aligned assessment is still in draft state
- **THEN** learners MUST NOT receive it through governed delivery surfaces

#### Scenario: Review state requires readiness visibility
- **WHEN** staff moves curriculum content into review
- **THEN** the system SHALL expose readiness status, missing academic-quality fields, and source compliance context for reviewers

#### Scenario: Published state is learner-safe
- **WHEN** curriculum content reaches published state
- **THEN** the system SHALL treat it as learner-deliverable only if readiness and governance requirements are satisfied
