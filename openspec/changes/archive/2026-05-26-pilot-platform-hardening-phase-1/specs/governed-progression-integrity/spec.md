## MODIFIED Requirements

### Requirement: Governed lesson selection drives learner progression deterministically
The system SHALL use governed learner-visible lessons as the source of truth for governed segment advancement, unit completion, and course continuation, and SHALL preserve ordinary sequential advancement for non-governed lesson paths.

#### Scenario: Learner completes a governed segment
- **WHEN** a learner completes a segment in an approved-ready lesson path
- **THEN** the next segment is resolved from the governed learner-visible lesson sequence

#### Scenario: Governed unit contains stale draft or non-governed progress rows
- **WHEN** governed learner progression is evaluated for a unit that also contains stale draft or otherwise non-governed segment-progress rows
- **THEN** the system does not auto-activate those stale rows
- **AND** governed continuation is resolved only from the current governed learner-visible lesson sequence

#### Scenario: No governed next lesson exists
- **WHEN** the learner reaches a point where no approved-ready governed next lesson exists
- **THEN** the system does not advance into draft or unapproved content and instead returns an explicit governed unavailable outcome

#### Scenario: Non-governed unit progresses normally
- **WHEN** learner progression is evaluated for an ordinary non-governed unit with a remaining `NOT_STARTED` segment
- **THEN** the system auto-activates the next sequential segment rather than blocking advancement under governed-only rules
