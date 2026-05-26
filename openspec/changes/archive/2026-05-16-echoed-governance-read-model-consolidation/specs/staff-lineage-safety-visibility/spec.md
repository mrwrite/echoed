## MODIFIED Requirements

### Requirement: Staff and admin users SHALL have read-only lineage visibility
The system SHALL expose lineage and historical-safety context through bounded staff/admin read models, governance summary payloads, or governance surfaces. The visibility SHALL include predecessor or successor context, lineage coherence validation, learner-progress safety validation, assessment-evidence safety validation, aggregate course-level safety status, and structured blocking issues or warnings with affected entity type, identifier, and title, without introducing a CMS workflow.

#### Scenario: Staff inspect superseded course safety context
- **WHEN** a staff or admin user views curriculum governance information for a course with historical lineage
- **THEN** the system SHALL show read-only lineage and safety context
- **AND** the surface SHALL not expose publish, edit, or destructive workflow actions as part of this capability

#### Scenario: Staff requests lineage and safety validation results for a course
- **WHEN** an authorized staff/admin/content user requests the bounded lineage and safety contract for a course
- **THEN** the system SHALL return aggregate course lineage and safety status along with blocking issues and warnings from lineage coherence, learner-progress safety, and assessment-evidence safety validation
- **AND** the response SHALL remain read-only and MUST NOT mutate curriculum, progress, attempts, answers, events, mastery, certification, or reporting state

#### Scenario: Unified governance summary carries lineage and safety context
- **WHEN** an authorized staff-facing course governance summary is requested
- **THEN** the system SHALL include lineage and historical-safety section data within that summary payload
- **AND** it SHALL preserve the existing bounded lineage validation semantics rather than replacing them with a new workflow
