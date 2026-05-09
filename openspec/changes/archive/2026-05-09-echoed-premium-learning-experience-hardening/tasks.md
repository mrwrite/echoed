## 1. Canonical UX state foundation

- [x] 1.1 Define shared UX state contracts for loading, skeleton, blocked, unavailable, empty, error, retry, and resolved states.
- [x] 1.2 Introduce reusable primitives and rendering patterns that enforce canonical async and unavailable-state behavior.
- [x] 1.3 Add Storybook-aligned coverage or documentation for the canonical UX primitives and state variants.

## 2. Shell and navigation hardening

- [x] 2.1 Apply canonical readiness, loading, and unavailable-state rendering to the authenticated shell, header, sidebar, and entry flows.

## 3. Learner experience hardening

- [x] 3.1 Stabilize dashboard continuity and continue-learning behavior on top of governed delivery and canonical session readiness.
- [x] 3.2 Harden lesson and assessment immersion, progression clarity, and reduced-cognitive-overload behavior for learner-facing surfaces.
- [x] 3.3 Apply responsive and accessibility improvements to core learner flows without altering governed progression semantics.

## 4. Educator experience hardening

- [x] 4.1 Standardize educator loading, empty, unavailable, and retry states using the canonical UX state system.
- [x] 4.2 Improve responsive educator layout behavior for tablet and constrained desktop workflows.

## 5. Design-system and accessibility governance

- [x] 5.1 Add accessibility and global-readiness checks for keyboard access, screen-reader semantics, contrast, scalable type, and low-bandwidth behavior.

## 6. Operational UX integrity and verification

- [x] 6.1 Add regression coverage for shell readiness, unavailable-state rendering, responsive behavior, and authenticated transition consistency.
- [x] 6.2 Validate that no parallel shell, session, or governed-delivery UX system is introduced during implementation.

## Follow-Ups

- [ ] Harden responsive shell and navigation behavior across desktop, tablet, and mobile breakpoints
- [ ] Standardize route transition, pending, and retry behavior for authenticated navigation flows
- [ ] Harden educator shell continuity around organization context, learner visibility, assignment visibility, and assessment visibility
- [ ] Establish canonical typography, spacing, card hierarchy, semantic color, and interaction guidance
- [ ] Enforce Tailwind/reusable primitive conventions to reduce local styling drift
- [ ] Remove remaining duplicate route-local UX state interpretation where canonical authority already exists
- [ ] Improve mobile organization-switch/header context UX
- [ ] Decompose `lesson-viewer.component.html` into smaller reusable primitives
- [ ] Add a dedicated positive/success state primitive
- [ ] Standardize toast vs inline state-panel usage