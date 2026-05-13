# rollback-and-deprecation-boundaries Specification

## Purpose
TBD - created by archiving change echoed-historical-curriculum-lineage-and-safety. Update Purpose after archive.
## Requirements
### Requirement: Deprecation and archival SHALL be interpreted as safe historical states
The system SHALL treat deprecated or archived revisions as historically meaningful states rather than destructive removal signals. Deprecated or archived records MAY be blocked from current publishing workflows while remaining available for historical interpretation, safety validation, and reporting.

#### Scenario: Deprecated revision still has learner evidence
- **WHEN** a deprecated or archived curriculum revision still has associated learner progress or assessment evidence
- **THEN** the historical record SHALL remain available for safety interpretation and reporting
- **AND** the deprecation state SHALL not remove or rewrite the dependent learner records

### Requirement: Rollback semantics SHALL remain bounded and non-destructive
The system SHALL define rollback only as a bounded governance interpretation that identifies safe historical revisions and successor relationships. Rollback support SHALL not destructively replace current content or mutate learner records in this change.

#### Scenario: Staff inspect a previous revision as rollback candidate
- **WHEN** staff review historical lineage and deprecation context for a possible rollback decision
- **THEN** the system SHALL expose read-only historical safety information
- **AND** it SHALL not execute a publish replacement or learner-state reassignment

