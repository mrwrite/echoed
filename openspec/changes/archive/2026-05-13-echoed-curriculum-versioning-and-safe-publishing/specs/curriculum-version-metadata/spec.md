## ADDED Requirements

### Requirement: Additive curriculum revision metadata
EchoEd SHALL define additive revision metadata for pathway, course, unit, and lesson publishing without replacing the existing curriculum hierarchy.

#### Scenario: Revision metadata does not create a second curriculum engine
- **GIVEN** existing Course, Unit, Lesson, Activity, Source, and Assessment structures remain authoritative
- **WHEN** revision metadata is defined
- **THEN** it SHALL layer on top of existing entities rather than introduce a parallel versioned content tree
- **AND** it SHALL support current-version reference semantics, published revision tracking, and draft lineage expectations

#### Scenario: Learner-safe visibility boundaries are preserved
- **GIVEN** draft and published revisions exist conceptually
- **WHEN** learner delivery is evaluated
- **THEN** only learner-safe published references SHALL be eligible for learner delivery
- **AND** draft revision lineage SHALL remain staff/admin scoped

### Requirement: Revision metadata must remain compatible across the current hierarchy
EchoEd SHALL define revision compatibility expectations that preserve the current relationship between pathway, course, unit, lesson, and aligned assessment structures.

#### Scenario: Current hierarchy remains canonical
- **GIVEN** a course contains ordered units and lessons
- **WHEN** revision semantics are applied
- **THEN** the current Course -> Unit -> Lesson hierarchy SHALL remain the canonical curriculum structure
- **AND** revision metadata SHALL not replace governed ordering or learner sequencing authority
