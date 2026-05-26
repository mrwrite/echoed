## MODIFIED Requirements

### Requirement: Additive curriculum revision metadata
The system SHALL support additive revision metadata for curriculum and assessment entities without changing default learner behavior. Revision metadata SHALL include revision identity, revision status, optional revision notes or metadata, publication and deprecation timestamps, and safe lineage references where they can be added without rewriting the current model.

#### Scenario: Existing curriculum records are serialized after revision metadata expansion
- **WHEN** legacy curriculum or assessment records are serialized after additive revision metadata and lineage support are introduced
- **THEN** they SHALL preserve existing behavior with backward-compatible defaults
- **AND** optional lineage references SHALL remain nullable unless explicitly populated

#### Scenario: Lineage-aware revision metadata is invalid
- **WHEN** a record contains incoherent revision status or lineage metadata
- **THEN** read-only governance and safe-publish validators SHALL surface the issue
- **AND** learner delivery and historical evidence records SHALL remain unmodified
