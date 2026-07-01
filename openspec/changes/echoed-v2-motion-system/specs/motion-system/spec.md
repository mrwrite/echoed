## ADDED Requirements

### Requirement: Global Motion Tokens

EchoEd SHALL provide reusable global motion tokens and utility classes for fast, restrained SaaS motion.

#### Scenario: Components use motion utilities

- **WHEN** a V2 page uses global motion utilities
- **THEN** it can apply fade-in, slide-up, page-enter, card-enter, stagger, hover-lift, press, skeleton, shimmer, and focus-ring behavior without adding page-specific keyframes

### Requirement: Reduced Motion Accessibility

EchoEd SHALL respect `prefers-reduced-motion`.

#### Scenario: Reduced motion is enabled

- **WHEN** the user enables reduced-motion preferences
- **THEN** transform-based movement and shimmer animations are disabled
- **AND** focus visibility and state changes remain available

### Requirement: Behavior Preservation

The motion system SHALL be presentation-only.

#### Scenario: User interacts with V2 pages

- **WHEN** users navigate, submit forms, open lessons, update statuses, or load analytics
- **THEN** existing handlers, routes, services, APIs, and authorization behavior remain unchanged
