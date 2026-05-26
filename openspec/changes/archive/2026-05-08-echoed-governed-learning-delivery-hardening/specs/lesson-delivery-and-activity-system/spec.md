## MODIFIED Requirements

### Requirement: Student lesson delivery only includes approved, ready lessons
The existing lesson delivery system SHALL preserve current progress and activity behavior while restricting student delivery and learner progression to lessons that are both approved and academically ready through canonical governed lesson selection.

#### Scenario: Student requests a lesson that is still draft
- **WHEN** a student attempts to access a lesson whose `review_status` is `draft` or `reviewed`
- **THEN** the system does not deliver that lesson through student-facing APIs and returns an explicit governed unavailable outcome

#### Scenario: Student requests an approved lesson that fails readiness
- **WHEN** a lesson is marked `approved` but does not satisfy readiness evaluation
- **THEN** the system does not deliver that lesson through student-facing APIs and does not use it to drive learner progression

#### Scenario: Student completes an approved lesson
- **WHEN** a student interacts with a lesson that is approved and ready
- **THEN** the existing activity flow and progress tracking continue to work using the governed learner-visible lesson sequence without a separate governance-specific progress system

#### Scenario: Student starts a unit with mixed governed and draft lessons
- **WHEN** a unit contains a mixture of approved-ready and non-governed lessons
- **THEN** learner activity and progress are initialized only for the approved-ready governed lessons in the canonical learner-visible sequence
