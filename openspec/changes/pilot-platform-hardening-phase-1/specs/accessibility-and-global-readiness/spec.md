## ADDED Requirements

### Requirement: Pilot-critical surfaces preserve baseline contrast and focus visibility

The platform SHALL maintain readable contrast and visible focus treatment across the shared shell, student dashboard, teacher dashboard, and lesson runtime.

#### Scenario: User navigates a pilot-critical flow by keyboard
- **WHEN** a student or teacher moves through shell or lesson actions without a pointer
- **THEN** focus remains visible and the next interactive target is understandable

#### Scenario: User reads core dashboard and lesson content
- **WHEN** student or teacher core-flow text is rendered in the pilot experience
- **THEN** headings, body text, status labels, and primary actions remain readable without low-contrast ambiguity
