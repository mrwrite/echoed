# unavailable-lesson-delivery-states Specification

## Purpose
TBD - created by archiving change echoed-governed-learning-delivery-hardening. Update Purpose after archive.
## Requirements
### Requirement: Learner delivery uses explicit unavailable states when governed content is not deliverable
The system SHALL return explicit institution-safe unavailable outcomes when a learner-facing request cannot be satisfied by an approved-ready governed lesson path, and the learner experience SHALL render those outcomes through a canonical blocked or unavailable presentation rather than route-local fallback content.

#### Scenario: Student requests a lesson that is not governed-deliverable
- **WHEN** a student requests a lesson that is draft, reviewed, or otherwise not approved and ready
- **THEN** the system returns an explicit unavailable outcome instead of delivering that lesson

#### Scenario: Unit has no approved-ready learner-visible lessons
- **WHEN** a learner attempts to begin or continue delivery for a unit with no approved-ready lessons
- **THEN** the system returns an unavailable or pending-review outcome instead of silently falling back to draft content

### Requirement: Educator audiences retain diagnostic visibility for unavailable learner states
The system SHALL preserve educator-facing visibility into why learner delivery is unavailable while protecting learners from draft-state ambiguity, and SHALL allow educator-facing UX surfaces to render operational diagnostics without changing learner-safe delivery rules.

#### Scenario: Educator inspects blocked learner delivery
- **WHEN** an educator or reviewer inspects a lesson or course path that is unavailable to learners because governance is incomplete
- **THEN** the educator-facing experience may expose governance status and readiness context needed for remediation

#### Scenario: Learner encounters unavailable governed content
- **WHEN** a learner encounters an unavailable governed lesson state
- **THEN** the learner experience does not expose draft-state ambiguity or instructor-only governance detail

