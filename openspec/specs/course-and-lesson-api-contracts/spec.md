# course-and-lesson-api-contracts Specification

## Purpose
TBD - created by archiving change echoed-content-review-governance. Update Purpose after archive.
## Requirements
### Requirement: Lesson APIs return audience-appropriate governance data
The existing lesson API contracts SHALL remain compatible while applying centralized governance-aware filtering, explicit learner-unavailable behavior, and field visibility based on the caller's audience.

#### Scenario: Authoring user requests a lesson
- **WHEN** an administrator, reviewer, or teacher requests a lesson through an authoring-capable endpoint
- **THEN** the system returns the full lesson, including draft or reviewed status and any educator-visible fields appropriate to that audience

#### Scenario: Student requests a governed lesson
- **WHEN** a student requests a lesson through a learner-facing endpoint
- **THEN** the system returns the lesson only if it is approved and ready, and suppresses educator-only fields

#### Scenario: Student requests a lesson that is not learner-deliverable
- **WHEN** a student requests a lesson that is not approved and ready
- **THEN** the system returns an explicit unavailable learner outcome rather than substituting draft content or an arbitrary sibling lesson

### Requirement: Course APIs filter nested lessons consistently for students
The existing course API contracts SHALL apply the same canonical governance visibility rules to nested lesson data as direct learner lesson endpoints.

#### Scenario: Student requests a course with mixed lesson statuses
- **WHEN** a course contains draft, reviewed, approved-not-ready, and approved-ready lessons
- **THEN** the student-facing course response includes only lessons that are approved and ready in the governed learner-visible sequence

#### Scenario: Teacher requests the same course
- **WHEN** an authorized teacher or administrator requests a course that contains mixed lesson statuses
- **THEN** the response includes all lessons needed for authoring, review, and instructional inspection

#### Scenario: Student requests a course unit with no learner-deliverable lessons
- **WHEN** a course unit has no approved-ready governed lessons
- **THEN** the learner-facing API does not silently include draft lessons and instead exposes an explicit unavailable or pending-review delivery state according to the endpoint contract

