## ADDED Requirements

### Requirement: Pilot-critical authenticated flows use canonical state messaging

The platform SHALL use user-friendly canonical state messaging across shell entry, student dashboard, teacher dashboard, and lesson runtime flows.

#### Scenario: Authenticated content is still loading
- **WHEN** a pilot-critical student or teacher surface is waiting for authoritative data
- **THEN** the visible loading state explains what is being prepared and avoids leaving stale content as the apparent current state

#### Scenario: Authenticated content resolves with no data
- **WHEN** a pilot-critical surface legitimately has no relevant data yet
- **THEN** the platform renders an intentional empty state that is distinct from blocked or failed behavior

### Requirement: Governed blocked and generic failure states remain distinct in pilot flows

The platform SHALL keep governed blocked outcomes distinct from generic runtime failures in learner-facing lesson delivery.

#### Scenario: Governed lesson cannot continue
- **WHEN** the lesson runtime resolves a governed blocked or unavailable outcome
- **THEN** the learner sees governed-specific guidance rather than a generic technical error state
