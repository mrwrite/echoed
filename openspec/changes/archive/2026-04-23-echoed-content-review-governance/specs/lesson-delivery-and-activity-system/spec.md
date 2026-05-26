## ADDED Requirements

### Requirement: Student lesson delivery only includes approved, ready lessons
The existing lesson delivery system SHALL preserve current progress and activity behavior while restricting student delivery to lessons that are both approved and academically ready.

#### Scenario: Student requests a lesson that is still draft
- **WHEN** a student attempts to access a lesson whose `review_status` is `draft` or `reviewed`
- **THEN** the system does not deliver that lesson through student-facing APIs

#### Scenario: Student requests an approved lesson that fails readiness
- **WHEN** a lesson is marked `approved` but does not satisfy readiness evaluation
- **THEN** the system does not deliver that lesson through student-facing APIs

#### Scenario: Student completes an approved lesson
- **WHEN** a student interacts with a lesson that is approved and ready
- **THEN** the existing activity flow and progress tracking continue to work without a separate governance-specific progress system
