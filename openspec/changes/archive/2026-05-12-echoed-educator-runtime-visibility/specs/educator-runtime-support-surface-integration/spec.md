## ADDED Requirements

### Requirement: Runtime support visibility integrates into existing educator surfaces
The system SHALL surface educator runtime support visibility through existing teacher/admin dashboard or reporting surfaces without creating a separate educator product area by default.

#### Scenario: Teacher dashboard renders learner support summaries
- **WHEN** runtime support data is available for flagship learners
- **THEN** the existing teacher-facing surface SHALL render bounded learner support summaries using current educator UI patterns

#### Scenario: Educator surfaces show canonical loading and empty states
- **WHEN** educator runtime support data is loading or no flagship support data is available
- **THEN** the educator surface SHALL use existing premium UX state primitives for loading, empty, error, and retry states

#### Scenario: Existing educator routes remain unchanged
- **WHEN** educator runtime support visibility is implemented
- **THEN** the existing teacher/admin route structure SHALL remain unchanged unless an additive read-only route is strongly justified
