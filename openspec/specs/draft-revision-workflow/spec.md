# draft-revision-workflow Specification

## Purpose
TBD - created by archiving change echoed-curriculum-versioning-and-safe-publishing. Update Purpose after archive.
## Requirements
### Requirement: Draft revision workflow must remain bounded and staff-facing
EchoEd SHALL define draft revision creation, preview, and publish replacement semantics without introducing a full CMS or workflow engine.

#### Scenario: Draft revisions remain staff/admin scoped
- **GIVEN** a staff or admin user creates or inspects a draft revision
- **WHEN** learner delivery is evaluated
- **THEN** the draft SHALL remain staff/admin visible only
- **AND** it SHALL not alter learner-facing governed delivery until a safe publish action is explicitly completed in a future implementation phase

#### Scenario: Preview is bounded and safe
- **GIVEN** a draft revision exists for staff review
- **WHEN** preview expectations are defined
- **THEN** preview SHALL be bounded to staff/admin users
- **AND** it SHALL not mutate learner progression, evidence, or certification records

### Requirement: Rollback expectations must preserve historical trust
EchoEd SHALL define bounded rollback semantics that favor learner safety over destructive reversal.

#### Scenario: Rollback does not rewrite evidence history
- **GIVEN** a published revision needs to be replaced or reverted
- **WHEN** rollback expectations are applied
- **THEN** rollback SHALL preserve historical learner evidence and prior delivery interpretation
- **AND** it SHALL not function as a branching curriculum tree or destructive reset

