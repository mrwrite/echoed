# course-governance-summary-read-model Specification

## Purpose
TBD - created by archiving change echoed-governance-read-model-consolidation. Update Purpose after archive.
## Requirements
### Requirement: Staff users SHALL receive one unified course governance summary payload
The system SHALL expose one canonical, staff-facing, read-only course governance summary payload that aggregates publish readiness, safe-publish validation, lineage safety visibility, competency-evidence integrity, and runtime intervention recommendation context for a single course.

#### Scenario: Authorized staff requests a course governance summary
- **WHEN** an authorized staff, admin, teacher, or content user requests governance context for a course
- **THEN** the system SHALL return one course-scoped governance payload
- **AND** that payload SHALL include bounded sections for publish readiness, safe-publish validation, lineage safety, competency integrity, and runtime intervention recommendations

#### Scenario: Summary payload preserves course readability
- **WHEN** the course governance summary is returned
- **THEN** each section SHALL include a bounded aggregate status and structured issue or warning context
- **AND** the payload SHALL remain staff-readable rather than an unstructured dump of raw validator internals

### Requirement: Unified governance summary SHALL preserve section semantics
The system SHALL keep each aggregated governance concern semantically distinct inside the unified payload so staff can interpret publish, safety, evidence, and runtime concerns without ambiguity.

#### Scenario: Summary contains multiple governance concerns
- **WHEN** a course has publish-readiness blockers, lineage warnings, and runtime recommendation context at the same time
- **THEN** the unified payload SHALL preserve those as separate bounded sections
- **AND** it SHALL not flatten them into one undifferentiated issue list

#### Scenario: Summary reflects no-issue sections without hiding them
- **WHEN** one governance section has no blocking issues or warnings
- **THEN** the summary SHALL still include that section with its bounded status
- **AND** staff SHALL not have to infer section absence from missing keys or omitted reads

### Requirement: Unified governance summary SHALL remain staff-only and read-only
The system SHALL restrict the unified course governance summary to authorized staff-facing contexts and SHALL NOT use summary evaluation to mutate curriculum, progression, assessment, certification, or reporting state.

#### Scenario: Learner requests the unified governance summary
- **WHEN** a learner or student user attempts to access the course governance summary
- **THEN** the system SHALL deny access or withhold the staff-only summary according to existing authorization boundaries
- **AND** learner-facing contracts SHALL remain unchanged

#### Scenario: Summary evaluation reads without side effects
- **WHEN** the course governance summary is computed
- **THEN** the system SHALL only read existing governance, lineage, competency, and runtime data
- **AND** it SHALL not create or update curriculum, publish, progress, attempt, mastery, certification, or reporting records

