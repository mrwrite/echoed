# governed-learner-delivery Specification

## Purpose
TBD - created by archiving change echoed-governed-learning-delivery-hardening. Update Purpose after archive.
## Requirements
### Requirement: Learner delivery uses one canonical governed lesson-selection flow
The system SHALL use one authoritative governed lesson-selection flow for learner-facing lesson delivery across direct lesson fetch, nested course delivery, start-course behavior, and progress-related learner resolution.

#### Scenario: Student requests a course with mixed lesson governance states
- **WHEN** a student requests a course that contains draft, reviewed, approved-not-ready, and approved-ready lessons
- **THEN** the system returns learner-visible lesson data using the same canonical governed lesson-selection logic that applies to all other learner delivery paths

#### Scenario: Student requests a direct lesson
- **WHEN** a student requests a lesson through a learner-facing lesson endpoint
- **THEN** the system resolves learner eligibility through the same governed lesson-selection flow used by learner-facing course delivery

#### Scenario: Student starts or resumes governed delivery
- **WHEN** the platform resolves the next learner lesson during start-course or continuation behavior
- **THEN** the system uses the same governed lesson-selection flow rather than raw route-local lesson enumeration

### Requirement: Governance policy is centralized in the existing governance layer
The system SHALL centralize learner visibility, approved-ready determination, governed selection, and audience-aware learner delivery rules in the existing governance policy layer rather than duplicating those decisions in route modules.

#### Scenario: Multiple learner-facing routes require lesson eligibility
- **WHEN** `courses.py`, `lessons.py`, `start_course.py`, or progress-related flows need to determine learner-visible lessons
- **THEN** they delegate to canonical governance-layer behavior instead of reimplementing route-specific governance logic

#### Scenario: Governance rules evolve
- **WHEN** learner lesson eligibility rules change
- **THEN** the platform updates the governance policy layer without requiring divergent learner-visibility behavior across routes

