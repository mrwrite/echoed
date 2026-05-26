## ADDED Requirements

### Requirement: Lessons support source-backed curriculum metadata
The system SHALL represent source-backed curriculum using the existing `Source` relationship on lessons and SHALL expose citation and URL data through existing lesson and course APIs.

#### Scenario: Lesson includes linked sources
- **WHEN** a lesson has one or more linked sources
- **THEN** the existing lesson and course responses include those sources with citation text and URL when available

#### Scenario: Lesson viewer renders sources
- **WHEN** the lesson viewer receives a lesson with source data
- **THEN** it renders the lesson sources clearly at the bottom of the lesson presentation
