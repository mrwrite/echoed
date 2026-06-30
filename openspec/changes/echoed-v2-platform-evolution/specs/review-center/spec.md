# review-center Specification

## ADDED Requirements

### Requirement: Review Center SHALL centralize human governance workflows
EchoEd SHALL introduce Review Center as the unified surface for reviewing lessons, artifacts, products, generated drafts, and source readiness.

#### Scenario: Reviewer opens Review Center
- **WHEN** a reviewer opens Review Center
- **THEN** EchoEd displays reviewable items with type, status, owner, source coverage, readiness, and required decision

#### Acceptance Criteria
- Current lesson review behavior remains authoritative for lessons.
- Generated artifacts are reviewable before publishing.
- Review Center does not bypass role permissions.

### Requirement: Review decisions SHALL be auditable
Review workflows SHALL record who reviewed an item, what decision was made, and when the decision occurred.

#### Scenario: Artifact is approved
- **WHEN** an authorized reviewer approves an artifact
- **THEN** EchoEd records the reviewer, decision, timestamp, and target item

#### Acceptance Criteria
- Review records are additive.
- Approval of an artifact does not automatically bypass lesson readiness.

## MODIFIED Requirements

### Requirement: Lesson governance SHALL remain intact inside Review Center
Existing lesson review status and readiness checks SHALL be reused in Review Center.

#### Scenario: Lesson is not source-ready
- **WHEN** a reviewer inspects a lesson missing required readiness data
- **THEN** Review Center surfaces the readiness issue and prevents learner publishing according to existing governance rules

#### Acceptance Criteria
- Existing lesson governance tests remain valid.
- Review Center uses existing readiness helpers where possible.

