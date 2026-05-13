# historical-lineage-metadata Specification

## Purpose
TBD - created by archiving change echoed-historical-curriculum-lineage-and-safety. Update Purpose after archive.
## Requirements
### Requirement: Curriculum entities SHALL support additive historical lineage metadata
The system SHALL support additive historical lineage metadata for `Course`, `Unit`, `Lesson`, and `Assessment` records without replacing the existing curriculum model. Supported lineage metadata SHALL allow a revision to identify a previous revision reference and, where safe, a successor reference while preserving backward-compatible defaults for existing records.

#### Scenario: Existing curriculum records have safe defaults
- **WHEN** historical lineage metadata is introduced for existing curriculum and assessment records
- **THEN** records SHALL remain valid without requiring lineage references
- **AND** the absence of lineage references SHALL be interpreted as a standalone current historical record rather than an error

### Requirement: Lineage metadata SHALL be coherent and bounded
The system SHALL define coherent lineage semantics for predecessor and successor references, revision labels, and revision statuses so staff and validators can interpret revision history without branching curriculum trees.

#### Scenario: Invalid lineage references are identified
- **WHEN** a curriculum or assessment record points to an incoherent predecessor or successor relationship
- **THEN** the system SHALL surface a lineage safety issue through read-only validation
- **AND** the issue SHALL not mutate learner, evidence, or curriculum records

