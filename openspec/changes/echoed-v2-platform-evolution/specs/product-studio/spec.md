# product-studio Specification

## ADDED Requirements

### Requirement: Product Studio SHALL become the flagship creator workflow
EchoEd SHALL introduce Product Studio as the primary guided workflow for creating, generating, reviewing, approving, publishing, and delivering learning products.

#### Scenario: Creator starts a product
- **WHEN** a creator opens Product Studio
- **THEN** EchoEd presents a product creation workflow that starts with product type and can reuse the existing course creation path

#### Acceptance Criteria
- Existing course wizard behavior remains available.
- Product Studio can initially support only course-backed products.
- Product Studio does not bypass lesson governance or readiness.

### Requirement: Product Studio SHALL follow the V2 creation sequence
Product Studio SHALL organize creation around:

```text
Create Product
-> Choose Product Type
-> Connect Project
-> Import Knowledge Sources
-> Analyze
-> Generate
-> Review
-> Approve
-> Publish
-> Deliver
```

#### Scenario: Phase 1 route exists before all steps are implemented
- **WHEN** a user opens Product Studio during Phase 1
- **THEN** implemented steps route to existing authoring surfaces
- **AND** unavailable future steps show clear placeholder states

#### Acceptance Criteria
- Placeholders do not create fake data.
- Current course creation remains functional.
- Future phases can replace placeholders incrementally.

## MODIFIED Requirements

### Requirement: Course wizard SHALL be embedded rather than replaced
The current course wizard SHALL be reused as the first Product Studio implementation path.

#### Scenario: Creator edits an existing course
- **WHEN** a creator edits a course-backed product
- **THEN** EchoEd can route into the existing course wizard with product-aware context

#### Acceptance Criteria
- Existing course create/edit tests remain valid.
- Existing course APIs remain valid.

