## ADDED Requirements

### Requirement: Teacher-facing lesson views expose instructional guidance
The system SHALL use the existing `teacher_notes` and `discussion_questions` lesson fields as the educator guidance layer and SHALL keep that guidance out of student-facing lesson views.

#### Scenario: Teacher-led lesson view is rendered
- **WHEN** the lesson viewer is operating in teacher-led mode
- **THEN** it displays `teacher_notes` and `discussion_questions` when they are present on the lesson

#### Scenario: Student lesson view is rendered
- **WHEN** the lesson viewer is operating in learner mode or a student-facing payload is returned
- **THEN** `teacher_notes` and `discussion_questions` are hidden from the student experience
