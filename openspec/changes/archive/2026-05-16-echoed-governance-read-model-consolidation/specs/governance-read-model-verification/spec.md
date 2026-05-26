## ADDED Requirements

### Requirement: Governance summary consolidation SHALL have focused regression coverage
The implementation SHALL include focused regression coverage for unified payload shape, staff access, learner denial, read-only behavior, frontend request reduction, and preservation of section-specific validator correctness.

#### Scenario: Tests verify unified payload shape
- **WHEN** the consolidated course governance summary is exercised in regression tests
- **THEN** the tests SHALL verify the presence of bounded publish-readiness, safe-publish, lineage-safety, competency-integrity, and runtime-intervention sections
- **AND** the tests SHALL confirm the payload is course-scoped and staff-readable

#### Scenario: Tests verify staff access and learner denial
- **WHEN** authorization behavior for the governance summary is tested
- **THEN** the tests SHALL confirm authorized staff-facing roles can access the summary
- **AND** learner or student requests SHALL be denied or withheld according to existing boundaries

### Requirement: Verification SHALL prove read-only non-mutation behavior
The implementation SHALL verify that governance summary evaluation does not mutate progression, assessment, certification, or reporting state.

#### Scenario: Summary evaluation does not mutate progression
- **WHEN** the unified governance summary is evaluated in regression tests
- **THEN** the tests SHALL confirm no mutation to governed learner progression or related course progress state
- **AND** the tests SHALL confirm evaluation remains read-only

#### Scenario: Summary evaluation does not mutate assessment or reporting state
- **WHEN** the unified governance summary is evaluated in regression tests
- **THEN** the tests SHALL confirm no mutation to attempts, evidence, mastery, certifications, or reporting outputs
- **AND** the tests SHALL confirm existing individual validators continue to behave correctly

### Requirement: Verification SHALL cover request-consolidation behavior
The implementation SHALL verify that staff dashboard consumption can reduce per-course governance request fan-out without breaking the existing bounded sections.

#### Scenario: Frontend request reduction is asserted
- **WHEN** a staff governance surface adopts the unified course governance summary
- **THEN** regression coverage SHALL verify that one course governance payload can replace multiple per-course governance requests
- **AND** the tests SHALL confirm the surface still renders the intended sections
