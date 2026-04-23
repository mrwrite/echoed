## ADDED Requirements

### Requirement: Academic quality aligns with existing lesson governance
The system SHALL align academic lesson structure and source-backed curriculum expectations with the existing lesson governance rules in `lesson_governance.py` rather than introducing a separate review or readiness system.

#### Scenario: Lesson is evaluated for readiness
- **WHEN** existing lesson governance evaluates a lesson for approval readiness
- **THEN** it uses the same academic lesson structure and source expectations that define an academically complete lesson

#### Scenario: Student and teacher lesson visibility is determined
- **WHEN** lesson payloads are serialized for student or teacher contexts
- **THEN** the system uses the existing governance layer to determine what academic and educator-only fields are visible
