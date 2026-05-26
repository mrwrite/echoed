## ADDED Requirements

### Requirement: Lesson presentation follows a classroom-style sequence
The system SHALL present lesson instructional sections in the sequence `hook`, `content`, `guided_practice`, `independent_practice`, and `assessment` while preserving the existing lesson activity flow.

#### Scenario: Lesson contains all instructional sections
- **WHEN** the lesson viewer renders a lesson with all supported instructional sections
- **THEN** it presents those sections in the defined classroom sequence

#### Scenario: Lesson contains only some instructional sections
- **WHEN** the lesson viewer renders a lesson with only a subset of instructional sections
- **THEN** it preserves the defined ordering for the sections that are present and does not break existing activity rendering
