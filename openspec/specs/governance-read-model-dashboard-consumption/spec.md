# governance-read-model-dashboard-consumption Specification

## Purpose
TBD - created by archiving change echoed-governance-read-model-consolidation. Update Purpose after archive.
## Requirements
### Requirement: Staff dashboards SHALL consume one governance payload per course
The system SHALL allow existing staff/admin/teacher governance surfaces to request one course governance summary payload per course instead of issuing separate per-course reads for each governance section.

#### Scenario: Staff dashboard renders governance sections for a course
- **WHEN** a staff-facing dashboard needs publish, safe-publish, lineage, competency, and runtime governance context for one course
- **THEN** the frontend SHALL be able to consume one unified course governance payload
- **AND** it SHALL not require separate per-course requests for each of those concerns by default

#### Scenario: Existing surfaces incrementally adopt the summary payload
- **WHEN** a staff governance surface is updated to the consolidated summary model
- **THEN** it SHALL keep its existing bounded course governance scope
- **AND** it SHALL not require workflow or action-surface expansion to use the new payload

### Requirement: Dashboard consumption SHALL preserve current bounded governance sections
The system SHALL preserve the existing staff-readable governance sections initially even when their data comes from one aggregated payload.

#### Scenario: Aggregated payload feeds existing UI sections
- **WHEN** a staff/admin course governance surface switches to the consolidated summary contract
- **THEN** existing publish-readiness, safe-publish, lineage, competency, and runtime sections SHALL remain separately renderable
- **AND** staff SHALL not lose section-specific interpretation because of payload consolidation

#### Scenario: Aggregated payload does not imply new actions
- **WHEN** the frontend consumes the unified course governance summary
- **THEN** the surface SHALL remain read-only for this capability
- **AND** it SHALL not add publish, rollback, grading, messaging, assignment, or intervention workflow controls

