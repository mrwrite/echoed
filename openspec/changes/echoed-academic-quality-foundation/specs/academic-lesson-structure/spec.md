## ADDED Requirements

### Requirement: Lessons expose the academic lesson structure
The system SHALL use the existing `Lesson` model and lesson APIs to represent an academic lesson structure that includes `learning_objectives`, `key_concepts`, `hook`, `content`, `guided_practice`, `independent_practice`, and `assessment`.

#### Scenario: Authoring user requests a lesson
- **WHEN** a teacher or administrator reads a lesson through the existing lesson or course APIs
- **THEN** the response includes the lesson structure fields when they are present on the lesson

#### Scenario: Lesson viewer renders an instructional lesson
- **WHEN** the frontend lesson viewer receives a lesson with instructional structure fields
- **THEN** it renders those sections in the intended classroom sequence without requiring a new lesson system
