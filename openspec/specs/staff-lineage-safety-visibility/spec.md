# staff-lineage-safety-visibility Specification

## Purpose
TBD - created by archiving change echoed-historical-curriculum-lineage-and-safety. Update Purpose after archive.
## Requirements
### Requirement: Staff and admin users SHALL have read-only lineage visibility
The system SHALL expose lineage and historical-safety context through bounded staff/admin read models or governance surfaces. The visibility SHALL include predecessor or successor context, safety warnings, and historical interpretation cues without introducing a CMS workflow.

#### Scenario: Staff inspect superseded course safety context
- **WHEN** a staff or admin user views curriculum governance information for a course with historical lineage
- **THEN** the system SHALL show read-only lineage and safety context
- **AND** the surface SHALL not expose publish, edit, or destructive workflow actions as part of this capability

### Requirement: Learner-facing serialization SHALL remain lineage-safe
The system SHALL keep learner-facing serialization and governed delivery free from staff-only lineage warnings and administrative historical-safety metadata unless a separate learner-safe requirement explicitly adds them later.

#### Scenario: Learner fetches governed curriculum data after lineage support exists
- **WHEN** learner-facing curriculum or progress data is serialized
- **THEN** staff-only lineage warnings and administrative safety fields SHALL not be exposed
- **AND** existing learner-safe delivery behavior SHALL remain unchanged

