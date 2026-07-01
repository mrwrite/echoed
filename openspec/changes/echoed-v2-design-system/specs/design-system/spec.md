## ADDED Requirements

### Requirement: Premium Visual Tokens

EchoEd SHALL provide a shared visual token layer for a dark luxury V2 experience using midnight backgrounds, soft purple, warm gold, azure accents, frosted glass panels, soft shadows, and rounded surfaces.

#### Scenario: Existing pages inherit premium styling

- **WHEN** a V2 page uses existing `.ee-*` shared classes
- **THEN** the page renders with the premium EchoEd V2 visual language
- **AND** no route, API, or business behavior is changed

### Requirement: Reusable Experience Components

EchoEd SHALL provide reusable presentational components for EECard, EEHero, EESection, EEButton, EEBadge, EEMetric, EEInput, EEFormSection, EEStatCard, EETimeline, EEEmptyState, EEStepper, EETag, and EENavigationCard.

#### Scenario: Components are presentation-only

- **WHEN** a page imports an EchoEd Experience component
- **THEN** the component accepts projected content or simple inputs
- **AND** it does not perform API calls, route changes, authorization checks, or business mutations

### Requirement: Consistent V2 Surface Polish

Workspace, Product Studio, Review Center, Learner Portal, and Analytics SHALL use shared visual language for headers, cards, metrics, badges, forms, empty states, and lists.

#### Scenario: V2 pages keep existing behavior

- **WHEN** a user interacts with an existing V2 form, button, link, or data panel
- **THEN** the existing handlers and routes continue to be used
- **AND** the change is limited to layout, hierarchy, color, spacing, and motion
