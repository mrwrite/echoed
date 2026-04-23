# lesson-readiness-validation Specification

## Purpose
TBD - created by archiving change echoed-content-review-governance. Update Purpose after archive.
## Requirements
### Requirement: Lessons expose academic readiness results
The system SHALL evaluate lesson readiness from the existing lesson content and linked sources without introducing a separate lesson-readiness model.

#### Scenario: Lesson includes all required academic elements
- **WHEN** a lesson has a title, an objective or learning objectives, at least one key concept, populated instructional flow sections, and at least one cited source
- **THEN** the system marks the lesson as ready for governance checks

#### Scenario: Lesson is missing academic completeness requirements
- **WHEN** a lesson lacks one or more required instructional or source elements
- **THEN** the system returns a readiness result that identifies the missing elements

### Requirement: Review-state promotion requires readiness
The system SHALL block transitions into reviewer-controlled lesson states unless the lesson satisfies the academic readiness rules.

#### Scenario: Reviewer attempts to mark an incomplete lesson as reviewed
- **WHEN** a lesson update requests `review_status` of `reviewed` and the lesson fails readiness evaluation
- **THEN** the system rejects the update and returns the readiness deficiencies

#### Scenario: Reviewer attempts to approve an incomplete lesson
- **WHEN** a lesson update requests `review_status` of `approved` and the lesson fails readiness evaluation
- **THEN** the system rejects the update and returns the readiness deficiencies

