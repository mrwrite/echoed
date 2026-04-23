## ADDED Requirements

### Requirement: Teacher-only lesson notes are not exposed to students
The system SHALL treat `teacher_notes` as staff-only lesson content in both backend responses and frontend rendering.

#### Scenario: Student requests a lesson
- **WHEN** a student receives a lesson payload through a student-facing lesson or course API
- **THEN** the response excludes or nulls `teacher_notes`

#### Scenario: Teacher views a lesson
- **WHEN** an authorized teacher or administrator views the same lesson through an authoring-capable surface
- **THEN** the response includes `teacher_notes`

### Requirement: Discussion questions remain learner-visible
The system SHALL continue exposing `discussion_questions` as part of normal lesson delivery for both student and staff viewers.

#### Scenario: Student opens an approved lesson
- **WHEN** a student views a lesson that is available for delivery
- **THEN** the lesson includes any configured `discussion_questions`

#### Scenario: Frontend renders a learner lesson view
- **WHEN** the lesson viewer is operating in learner mode
- **THEN** it displays discussion questions and suppresses teacher-only notes
