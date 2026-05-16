# Design: EchoEd Demo Readiness and Flagship Experience

## Context

EchoEd now has enough platform depth that the quality of a live demo depends less on adding new systems and more on making existing systems deterministic. The flagship “Introduction to Africa” pathway already anchors governed delivery, mastery evidence, runtime support, and staff-facing visibility. The missing piece is reliable orchestration of those systems into one reproducible demo environment.

This change treats demo readiness as an operational product surface. A strong demo is not fake behavior. It is a stable, bounded composition of real platform behavior seeded into predictable states.

## Goals

- Make the demo environment reproducible
- Make the flagship pathway presentation-stable for student, teacher, and admin roles
- Seed deterministic learner, mastery, runtime, and governance examples
- Provide a safe reset and setup path for repeated demos
- Preserve governed delivery, scoring, certification, reporting, auth, and permissions behavior
- Define polish work for the flagship experience without redesigning it yet

## Non-Goals

- Building new governance or versioning engines
- Adding demo-only business rules or role bypasses
- Replacing the current curriculum model
- Rewriting teacher, admin, or student UI in this change
- Expanding workflow systems around grading, interventions, or live classroom sync

## Architectural Direction

### 1. Deterministic Seeding Must Reuse Real Systems

Demo data must flow through the same:

- organization and membership model
- course, unit, and lesson structure
- governed learner delivery rules
- assessment and attempt recording model
- mastery and competency evidence model
- runtime intervention evaluation logic
- governance read and validation logic
- certification and reporting behavior

The demo should feel polished because seeded state is well chosen, not because production rules were bypassed.

### 2. Seed Archetypes Around Clear Learner Stories

The flagship course should reliably express a small set of demo learners:

- strong/mastered learner
- struggling learner
- ambiguous or monitor learner
- normal progression learner

These archetypes should be encoded through real lesson progress, attempts, answers, events, mastery evidence, and runtime recommendations. They should not be represented by synthetic labels alone.

### 3. Seed Runtime and Governance as Presentation Assets

The seeded environment should intentionally produce stable examples of:

- enrichment
- reteach
- review
- monitor
- normal

And stable examples of:

- publish readiness issues and non-issues
- safe publish examples
- lineage-safety examples
- competency evidence integrity examples

This gives teacher and admin demos predictable narrative value without adding new product features.

### 4. Reset Must Be Safe, Repeatable, and Bounded

The reset path should favor:

- idempotent or equivalent safe reseed behavior
- stable identities for demo orgs, users, courses, and flagship content
- cleanup and recreation rules that do not damage unrelated platform behavior
- a documented execution path that a demo operator can follow consistently

The implementation may reset and rebuild demo-scoped data where necessary, but it should remain additive and clearly bounded to the demo domain.

## Domain Design

### Deterministic Demo Foundation

The demo environment should define one canonical demo organization and a bounded set of demo users with stable roles and credentials. The flagship course should remain the canonical anchor for role-based walkthroughs. Seeded sections, enrollments, progress rows, attempts, mastery evidence, and runtime outcomes should remain consistent across reseeds.

### Flagship Demo State Orchestration

The seeded flagship experience should make the student story predictable:

- one learner shows strong completion and enrichment-ready behavior
- one learner shows struggling or reteach-needed behavior
- one learner shows ambiguous evidence and review or monitor behavior
- one learner shows steady normal progression

The same seeded evidence should support teacher and admin demo surfaces without route-specific hacks.

### Governance Demonstration Readiness

The seeded curriculum and evidence set should generate useful governance examples. That does not require a second governance engine. It requires choosing seeded content and evidence conditions that naturally trigger the existing validators and summary read models in stable ways.

### Operational Demo Stability

The demo path should be runnable through a small documented execution flow:

- initialize or reseed the demo environment
- verify canonical accounts and flagship content exist
- verify core learner and staff views are in expected states

This change should also expand regression tests around seeded behavior so demo stability is enforced over time.

### Polish Planning Without Redesign

This change should capture where flagship polish is still needed next:

- shell smoothness
- role landing experience
- showcase sequencing
- messaging and empty-state consistency
- visual rhythm across student, teacher, and admin stories

But this planning should remain documentation-level in this change unless specific non-disruptive polish tasks are later implemented.

## Risks and Trade-Offs

- Deterministic seeding can become brittle if it depends on too many incidental IDs or ordering assumptions
- Rich demo states can drift as runtime, mastery, or governance systems evolve
- Reset behavior can be dangerous if it is not strictly demo-scoped
- Too much demo specialization could diverge from real product behavior if not carefully bounded

## Mitigations

- Reuse canonical production logic instead of demo forks
- Keep demo state definitions explicit and versioned in seed code
- Scope reset behavior to clearly named demo entities
- Add regression tests around seeded archetypes, runtime states, governance states, and non-regression platform behavior

## Summary

EchoEd’s next demo win does not require more product breadth. It requires a deterministic, repeatable flagship environment that reliably shows what the platform already does well. This change hardens that environment while preserving real product behavior and setting up later polish work from a stable base.
