## MODIFIED Requirements

### Requirement: Published curriculum edits must distinguish minor and material changes
EchoEd SHALL define minor versus material change boundaries for published curriculum so safe republish behavior can preserve learner continuity and expose deterministic safe-publish concerns through the unified staff governance summary.

#### Scenario: Minor published edits remain continuity-safe
- **GIVEN** a published lesson receives a typo fix, formatting correction, or non-semantic source cleanup
- **WHEN** the edit is classified
- **THEN** it SHALL be treated as a minor change
- **AND** it SHALL not imply new learner progression semantics or historical evidence reinterpretation

#### Scenario: Material published edits require stronger governance
- **GIVEN** a published lesson changes instructional intent, required sequencing, evidence expectations, or core learner-facing meaning
- **WHEN** the edit is classified
- **THEN** it SHALL be treated as a material change
- **AND** safe publish warnings or blocking conditions SHALL reflect the continuity risk

#### Scenario: Unified governance summary includes safe-publish results
- **GIVEN** safe-publish warnings or blocking conditions exist for a course revision
- **WHEN** an authorized staff-facing governance summary is requested
- **THEN** the system SHALL expose those safe-publish concerns in the bounded summary payload
- **AND** it SHALL remain read-only without adding republish or rollback actions
