## ADDED Requirements

### Requirement: Course and lesson APIs surface academic-quality fields consistently
The existing course and lesson APIs SHALL expose the academic lesson structure fields, lesson sources, and governance-derived visibility behavior consistently across direct lesson reads and nested course lesson responses.

#### Scenario: Authoring user reads course or lesson data
- **WHEN** a teacher or administrator reads course or lesson data
- **THEN** the lesson payloads expose the same academic-quality fields in both direct lesson and nested course responses

#### Scenario: Student reads course or lesson data
- **WHEN** a student reads course or lesson data
- **THEN** the lesson payloads preserve governance-based visibility rules while still exposing the learner-safe academic lesson fields
