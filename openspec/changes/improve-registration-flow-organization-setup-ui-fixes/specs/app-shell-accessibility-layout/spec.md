## ADDED Requirements

### Requirement: Registration surfaces maintain readable contrast
The system SHALL present registration and organization-onboarding content with readable contrast for primary text, helper copy, warnings, form fields, and disabled or loading states across the supported page theme.

#### Scenario: Helper copy appears on dark registration surfaces
- **WHEN** registration or onboarding helper text is rendered over the page background and surrounding panels
- **THEN** the text remains visually readable and distinguishable from decorative background elements

#### Scenario: Error and disabled states appear during form interaction
- **WHEN** a registration or onboarding form displays an error, hint, or disabled submit state
- **THEN** the state styling remains readable and clearly communicates the control status

### Requirement: Sidebar layout remains stable across shell states
The system SHALL keep the authenticated shell layout aligned with the sidebar state so that navigation and page content remain usable on first paint and during collapsed or expanded transitions.

#### Scenario: Dashboard renders with expanded sidebar
- **WHEN** the authenticated shell renders with the sidebar expanded
- **THEN** the sidebar width and main content offset align without overlap or clipped content

#### Scenario: User collapses the sidebar
- **WHEN** the user collapses the sidebar while remaining in the authenticated shell
- **THEN** the main content reflows to the collapsed width and the visible navigation remains usable in its compact state

#### Scenario: Navigation loads after session bootstrap
- **WHEN** visible navigation sections resolve after session and permission bootstrap
- **THEN** the shell preserves a stable sidebar frame and does not shift content in a way that obscures navigation or primary page content
