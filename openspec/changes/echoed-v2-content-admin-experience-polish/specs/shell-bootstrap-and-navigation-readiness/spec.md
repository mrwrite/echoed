## ADDED Requirements

### Requirement: Premium workspace navigation presentation
The authenticated shell SHALL present V2 workspace navigation as a premium workspace rail with icon-led items, clear active states, readable labels, refined grouping, and a polished profile footer while preserving deterministic role-aware navigation.

#### Scenario: Sidebar renders workspace navigation
- **WHEN** the authenticated shell renders the workspace sidebar after bootstrap has resolved
- **THEN** navigation items show meaningful icons, unclipped labels, clear grouping, and a visible active state for the current route

#### Scenario: Sidebar is collapsed
- **WHEN** the sidebar is displayed in a collapsed or narrow state
- **THEN** the rail remains usable with icon-first affordances, accessible labels, and no clipped visible text

### Requirement: Premium command-center header presentation
The authenticated shell SHALL present a polished command-center header with clear breadcrumb/title hierarchy, refined organization selector styling, premium guided-tour action treatment, and improved user avatar presentation.

#### Scenario: Workspace route renders header
- **WHEN** a user opens a workspace/admin route in the authenticated shell
- **THEN** the header clearly communicates the current workspace context and primary command actions without changing route or authorization semantics

#### Scenario: Organization selector is available
- **WHEN** the organization selector is rendered
- **THEN** it is visually integrated with the premium header and remains keyboard accessible

### Requirement: Premium workspace shell background
The authenticated workspace shell SHALL use a refined premium background and content container system that supports readability, responsive layouts, and consistent page max-widths.

#### Scenario: Workspace page loads
- **WHEN** a workspace/admin page renders inside the authenticated shell
- **THEN** the background, content max-width, spacing, and surface hierarchy feel visually consistent with the approved premium EchoEd direction
