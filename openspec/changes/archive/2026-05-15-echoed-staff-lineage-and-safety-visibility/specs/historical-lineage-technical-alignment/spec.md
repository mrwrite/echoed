## MODIFIED Requirements

### Requirement: Historical lineage SHALL preserve the canonical governed curriculum architecture
The system SHALL implement lineage and historical-safety guarantees within the existing `Course`, `Unit`, `Lesson`, `Assessment`, governed delivery, runtime support, and assessment/mastery architecture. It SHALL not introduce a parallel curriculum engine, parallel progression system, destructive migration requirement, mutation endpoint, or workflow engine in order to expose staff lineage and safety visibility.

#### Scenario: Implementing lineage metadata and validation
- **WHEN** the system adds lineage metadata and historical-safety validation
- **THEN** it SHALL reuse the existing curriculum, governance, and reporting architecture
- **AND** it SHALL avoid a second curriculum storage or delivery system

#### Scenario: Implementing staff lineage and safety endpoint and UI visibility
- **WHEN** the system exposes staff lineage and safety results through backend contracts and governance UI
- **THEN** it SHALL preserve the existing `Course`/`Unit`/`Lesson`/`Assessment` models, safe-publish validators, and governed learner delivery flow
- **AND** it SHALL avoid route redesign, workflow orchestration, or destructive behavior

### Requirement: Historical lineage SHALL preserve auth and reporting boundaries
The system SHALL preserve existing auth/session authority, learner-safe serialization boundaries, and reporting compatibility when lineage-aware safety data is introduced.

#### Scenario: Staff visibility expands with lineage context
- **WHEN** lineage-aware safety fields are exposed for staff/admin use
- **THEN** the system SHALL keep access bounded by existing authorization patterns
- **AND** reporting compatibility SHALL remain additive rather than breaking existing consumers

#### Scenario: Staff lineage visibility is introduced through read-only governance contracts
- **WHEN** a staff-only lineage and safety endpoint or UI surface is added
- **THEN** it SHALL remain read-only and aligned with existing reporting and governance boundaries
- **AND** it SHALL not alter learner serialization, grading, certification, or governed delivery behavior
