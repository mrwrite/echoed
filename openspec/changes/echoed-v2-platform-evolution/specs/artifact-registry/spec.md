# artifact-registry Specification

## ADDED Requirements

### Requirement: Artifacts SHALL represent generated or uploaded knowledge outputs
EchoEd SHALL introduce Artifact as a durable, reviewable output produced by AI generation, manual upload, or authoring workflows.

Artifact types MAY include:

- outline
- documentation page
- lesson draft
- course draft
- playbook
- checklist
- download pack
- quiz draft
- source summary
- implementation guide

#### Scenario: AI generates a draft lesson artifact
- **WHEN** a generation run creates a lesson draft
- **THEN** EchoEd stores the output as an artifact before it becomes a learner-facing lesson

#### Acceptance Criteria
- Artifacts default to draft or review-required state.
- Artifacts do not become learner-deliverable without review or explicit publishing.
- Artifacts can reference sources and generation runs.

### Requirement: Artifact registry SHALL support packaging and review
The artifact registry SHALL let creators inspect, review, attach, publish, or package artifacts.

#### Scenario: Creator reviews artifact
- **WHEN** a creator opens an artifact
- **THEN** EchoEd shows artifact content, source references, generation metadata, review state, and attachment targets

#### Acceptance Criteria
- Artifact inspection does not alter course runtime behavior.
- Downloadable resources can be represented by artifacts in later phases.

## MODIFIED Requirements

### Requirement: Uploaded media and generated docs SHALL be eligible artifact sources
Existing upload/media behavior SHALL remain available and MAY be wrapped as artifacts where useful.

#### Scenario: Existing uploaded resource is attached to product
- **WHEN** a creator attaches an uploaded resource to a product
- **THEN** EchoEd can represent the attachment as an artifact/resource without changing the original upload path

#### Acceptance Criteria
- Existing upload tests remain valid.
- Artifact wrapping is additive.

