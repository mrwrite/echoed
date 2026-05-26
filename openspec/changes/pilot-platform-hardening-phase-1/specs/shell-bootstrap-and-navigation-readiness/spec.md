## ADDED Requirements

### Requirement: Pilot-critical shell entry and return paths remain visually stable

The platform SHALL keep the authenticated shell, header, sidebar, and primary content region stable across dashboard entry, role-aware navigation, and return-from-lesson transitions.

#### Scenario: Student returns from a lesson
- **WHEN** a student exits a lesson back to the dashboard
- **THEN** the dashboard re-enters through the resolved authenticated shell without broken navigation, contradictory role cues, or displaced primary content

#### Scenario: Teacher reaches the dashboard after login
- **WHEN** a teacher completes authenticated bootstrap
- **THEN** the header, sidebar, and dashboard layout render from resolved role and organization context without flashing stale navigation or partial shell states
