## ADDED Requirements

### Requirement: Premium Landing Page

EchoEd SHALL provide a premium marketing homepage suitable for investors, schools, enterprises, parents, and teachers.

#### Scenario: Visitor opens the homepage

- **WHEN** a visitor navigates to `/`
- **THEN** the page shows a large editorial hero, glass feature panel, gradient background, animated platform cards, feature grid, Today's Demo, Roadmap, Testimonials, Walkthrough, and CTA sections

### Requirement: Existing Navigation Preserved

The landing page SHALL preserve existing authentication and demo navigation entry points.

#### Scenario: Visitor uses landing links

- **WHEN** the visitor selects Sign in, Create account, Schedule Demo, or Launch Demo
- **THEN** the links use the existing `/login` and `/registration` route targets
- **AND** no backend, route, API, or authentication behavior is changed
