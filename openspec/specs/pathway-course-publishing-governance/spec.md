# pathway-course-publishing-governance Specification

## Purpose
TBD - created by archiving change echoed-curriculum-authoring-governance. Update Purpose after archive.
## Requirements
### Requirement: Publishing is governed at pathway, course, unit, and lesson scope
The system SHALL apply publish-readiness, deterministic ordering, learner availability, staff preview rules, and staff-facing governance summary visibility to pathway, course, unit, and lesson publishing without creating a separate curriculum engine.

#### Scenario: Staff can preview unpublished governed content
- **WHEN** authorized staff inspects draft or approved-but-unpublished content
- **THEN** the system SHALL allow staff preview without exposing the same content to learners

#### Scenario: Learners see unavailable content before publish
- **WHEN** governed content is not yet published for learners
- **THEN** learner-facing delivery SHALL continue to render canonical unavailable behavior instead of silently substituting other content

#### Scenario: Publishing requires deterministic ordering
- **WHEN** a pathway or course is prepared for publish
- **THEN** the system SHALL validate deterministic unit and lesson ordering before learner release

#### Scenario: Staff governance summary includes publish-readiness status
- **WHEN** an authorized staff-facing governance summary is requested for a course
- **THEN** the system SHALL include bounded publish-readiness status and issue context in the unified course governance payload
- **AND** it SHALL preserve the existing publish-readiness semantics rather than redefining them in the summary layer

