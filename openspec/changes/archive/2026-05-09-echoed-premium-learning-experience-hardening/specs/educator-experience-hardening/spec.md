## ADDED Requirements

### Requirement: Educator operational flows remain stable across organization and visibility changes
The platform SHALL preserve stable educator context for organization switching, learner visibility, assignments, and assessment operations using confirmed session and organization state.

#### Scenario: Educator changes active organization
- **WHEN** an educator switches organizations
- **THEN** the surrounding shell and operational views update from confirmed context without misleading intermediate visibility states

#### Scenario: Educator opens a learner or assessment context
- **WHEN** an educator navigates between learner, assignment, or assessment views
- **THEN** the platform preserves clear visibility boundaries and does not reinterpret state differently per route

### Requirement: Educator surfaces use responsive operational layouts
The platform SHALL preserve educator usability across desktop and tablet layouts without hiding critical status or workflow context.

#### Scenario: Educator works from a tablet-sized viewport
- **WHEN** educator operational views are rendered on a tablet or constrained laptop viewport
- **THEN** primary actions, state context, and workflow cues remain visible and operable

#### Scenario: Educator manages multiple operational panels
- **WHEN** a view includes filters, contextual status, and primary actions
- **THEN** the layout preserves hierarchy and avoids compressing critical controls into ambiguous overflow states

### Requirement: Educator UX uses canonical async and unavailable behavior
The platform SHALL render educator loading, unavailable, empty, and retry states through the same canonical UX state system used elsewhere, with educator-appropriate diagnostics.

#### Scenario: Educator data is temporarily unavailable
- **WHEN** an educator-facing surface cannot load its operational data
- **THEN** the platform shows a canonical state with enough diagnostic context for recovery without exposing implementation detail

#### Scenario: Educator inspects a governed blocked learner path
- **WHEN** an educator views a learner context that is blocked or unavailable
- **THEN** the educator sees stable operational context that explains the blocked state without route-local interpretation drift
