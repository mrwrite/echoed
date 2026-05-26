## ADDED Requirements

### Requirement: Published curriculum edits must distinguish minor and material changes
EchoEd SHALL define minor versus material change boundaries for published curriculum so safe republish behavior can preserve learner continuity.

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

### Requirement: Republish behavior must preserve governed learner continuity
EchoEd SHALL define republish semantics that allow current published references to evolve without destructive replacement of active or historical learner context.

#### Scenario: Republish does not override learner history
- **GIVEN** a new published revision becomes current for future delivery
- **WHEN** historical learner records are interpreted
- **THEN** previously earned learner progress, attempts, and evidence SHALL remain anchored to the experience that occurred
- **AND** republish behavior SHALL not hard-overwrite historical learner references
