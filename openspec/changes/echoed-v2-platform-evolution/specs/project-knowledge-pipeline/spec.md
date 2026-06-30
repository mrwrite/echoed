# project-knowledge-pipeline Specification

## ADDED Requirements

### Requirement: Projects SHALL group knowledge, generation, artifacts, and products
EchoEd SHALL introduce Project as the V2 container for knowledge sources, AI analysis, generation runs, artifacts, and products.

#### Scenario: Creator opens an empty project
- **WHEN** a creator opens a project with no sources
- **THEN** EchoEd shows an empty project state oriented around importing knowledge sources and creating products

#### Acceptance Criteria
- Projects belong to a workspace.
- Projects can exist before products are created.
- Projects do not replace courses.

### Requirement: Knowledge pipeline SHALL preserve source traceability
Knowledge moving through projects SHALL retain traceability from source to analysis, artifact, product, and learner-facing content.

#### Scenario: Artifact is generated from sources
- **WHEN** a generation run produces an artifact from selected knowledge sources
- **THEN** the artifact records which sources contributed to the output

#### Acceptance Criteria
- Existing lesson `Source` rows remain valid.
- Future `KnowledgeSource` records can link to existing lesson sources.
- No source-backed readiness behavior is weakened.

## MODIFIED Requirements

### Requirement: Lesson sources SHALL become reusable knowledge assets over time
Existing lesson-bound sources SHALL be eligible for mapping into project-level knowledge sources without deleting original source records.

#### Scenario: Existing course is wrapped by a project
- **WHEN** an existing course is associated with a project
- **THEN** its lesson sources can be surfaced as project knowledge sources
- **AND** lesson readiness continues to evaluate against the original lesson source data until migration is complete

#### Acceptance Criteria
- Existing lesson readiness tests remain green.
- Source migration is additive.

