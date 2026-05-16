# versioning-ux-and-governance-boundaries Specification

## Purpose
TBD - created by archiving change echoed-curriculum-versioning-and-safe-publishing. Update Purpose after archive.
## Requirements
### Requirement: Revision visibility must remain bounded to staff/admin governance surfaces
EchoEd SHALL keep versioning, lineage, and safe-publish visibility bounded to staff/admin governance contexts.

#### Scenario: Learners do not receive staff revision governance details
- **GIVEN** revision summaries, warnings, or safe publish concerns exist
- **WHEN** learner-facing surfaces are rendered
- **THEN** staff/admin governance details SHALL not be exposed to learners
- **AND** learner messaging, if any, SHALL remain safe, minimal, and continuity-preserving

#### Scenario: Lineage and historical safety warnings remain staff-scoped
- **GIVEN** lineage coherence issues, learner-progress safety risks, or assessment-evidence safety risks exist
- **WHEN** staff/admin governance surfaces are rendered
- **THEN** those lineage and historical-safety details SHALL remain bounded to authorized staff contexts
- **AND** learner-facing UI SHALL not render the same staff warning payloads or controls

### Requirement: Safe publish warnings must be understandable without a full authoring suite
EchoEd SHALL define bounded governance UX expectations for revision summaries, lineage context, publishing warnings, and unified course governance summary consumption.

#### Scenario: Staff can inspect readiness and revision concerns
- **GIVEN** staff/admin users need to inspect curriculum safety before publish or republish
- **WHEN** the bounded UX expectations are defined
- **THEN** the system SHALL support revision summaries, warnings, and learner-safety guidance
- **AND** it SHALL avoid full CMS workflow complexity in this initiative

#### Scenario: Staff sees lineage and safety issues beside governance sections
- **GIVEN** publish-readiness or safe-publish views already exist for staff users
- **WHEN** lineage and historical-safety visibility is rendered
- **THEN** the system SHALL show blocking issues, warnings, and affected entity context beside existing governance sections
- **AND** it SHALL not add publish, rollback, or mutation buttons as part of that visibility

#### Scenario: Existing staff sections consume one aggregated payload
- **GIVEN** staff governance surfaces already present publish, safe-publish, lineage, competency, or runtime sections
- **WHEN** those surfaces adopt the unified course governance summary payload
- **THEN** the system SHALL preserve the existing bounded section structure while reducing per-course request fan-out
- **AND** it SHALL not introduce workflow or action-surface expansion as part of that consolidation

