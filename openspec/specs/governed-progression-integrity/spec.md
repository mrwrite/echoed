# governed-progression-integrity Specification

## Purpose
TBD - created by archiving change echoed-governed-learning-delivery-hardening. Update Purpose after archive.
## Requirements
### Requirement: Learner progress is created only for governed learner-visible lessons
The system SHALL create learner segment and related progress rows only for lessons that are governed and learner-visible at the time delivery is initialized.

#### Scenario: Course unit contains draft or unapproved lessons
- **WHEN** a learner starts a course or a unit contains lessons that are not approved and ready
- **THEN** the system does not create learner segment progress for those non-governed lessons

#### Scenario: Course unit contains approved-ready lessons
- **WHEN** a learner starts a course whose next governed unit contains approved-ready lessons
- **THEN** the system creates progress rows only for the governed learner-visible lesson path

### Requirement: Governed lesson selection drives learner progression deterministically
The system SHALL use governed learner-visible lessons as the source of truth for segment advancement, unit completion, and course continuation.

#### Scenario: Learner completes a governed segment
- **WHEN** a learner completes a segment in an approved-ready lesson path
- **THEN** the next segment is resolved from the governed learner-visible lesson sequence

#### Scenario: No governed next lesson exists
- **WHEN** the learner reaches a point where no approved-ready governed next lesson exists
- **THEN** the system does not advance into draft or unapproved content and instead returns an explicit governed unavailable outcome

### Requirement: Governed progress remains institutionally auditable
The system SHALL preserve a trustworthy relationship between delivered learner content and stored learner progress so that institutions can rely on progress records as evidence of actual governed instruction.

#### Scenario: Institution audits learner progress
- **WHEN** an institution reviews learner progress data for a course
- **THEN** every learner-facing segment in the record corresponds to a lesson that was eligible for governed delivery when the segment path was created

#### Scenario: Educator views learner progression alongside governed content
- **WHEN** an educator inspects learner progress for a governed course
- **THEN** the educator can reconcile the learner's progress path with the governed learner-visible lesson sequence rather than a hidden draft sequence

