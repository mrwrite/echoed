# course-and-lesson-api-contracts Specification

## Purpose
TBD - created by archiving change echoed-content-review-governance. Update Purpose after archive.
## Requirements
### Requirement: Lesson APIs return audience-appropriate governance data
The existing lesson API contracts SHALL remain compatible while applying governance-aware filtering and field visibility based on the caller's role.

#### Scenario: Authoring user requests a lesson
- **WHEN** an administrator or teacher requests a lesson through an authoring-capable endpoint
- **THEN** the system returns the full lesson, including draft or reviewed status and any teacher-only fields

#### Scenario: Student requests a governed lesson
- **WHEN** a student requests a lesson through a student-facing endpoint
- **THEN** the system returns the lesson only if it is approved and ready, and suppresses teacher-only fields

### Requirement: Course APIs filter nested lessons consistently for students
The existing course API contracts SHALL apply the same governance visibility rules to nested lesson data as direct lesson endpoints.

#### Scenario: Student requests a course with mixed lesson statuses
- **WHEN** a course contains draft, reviewed, and approved lessons
- **THEN** the student-facing course response includes only lessons that are approved and ready

#### Scenario: Teacher requests the same course
- **WHEN** an authorized teacher or administrator requests a course that contains mixed lesson statuses
- **THEN** the response includes all lessons so authors and reviewers can inspect in-progress content

