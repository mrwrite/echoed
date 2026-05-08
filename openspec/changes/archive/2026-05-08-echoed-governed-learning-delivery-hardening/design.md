## Context

EchoEd already has the right core building blocks for institutionally trustworthy learning delivery: the existing lesson and course hierarchy, lesson readiness evaluation, constrained governance status transitions, learner progress tables, and audience-aware lesson serialization. The platform's current problem is not the absence of governance primitives; it is that those primitives are not yet the single authoritative source for every learner-facing delivery path.

The repository audit showed the same learner-delivery concept being resolved differently depending on the route. Course payloads, direct lesson fetches, start-course behavior, progress creation, and demo lesson delivery can currently diverge. In particular, progress can still be created from raw unit lessons instead of a governed learner-visible lesson set, and fallback behavior can preserve learner access to draft content when no approved-ready lesson exists.

This design keeps the current EchoEd architecture intact. It does not replace lessons, units, courses, governance, or progress. It hardens the seams between them so learner delivery, progression, and unavailability states become deterministic and institutionally auditable.

## Goals / Non-Goals

**Goals:**
- Establish one canonical governed lesson-selection flow for learner-facing delivery
- Ensure governed lesson-selection logic is reused by direct lesson fetch, nested course delivery, start-course behavior, and progress creation
- Guarantee that learner progress is created and advanced only from approved-ready lessons that are actually deliverable to learners
- Replace silent learner fallback-to-draft behavior with explicit institution-safe unavailable states
- Preserve educator, reviewer, and author visibility through centralized audience-aware serialization
- Make seeded demo environments reflect governed production delivery rather than bypassing it
- Add strong verification coverage for deterministic governed delivery behavior

**Non-Goals:**
- Rewriting the lesson, course, unit, or progress data model
- Introducing a second learner-delivery pipeline or a separate governance-only course system
- Expanding into grading, transcripts, mobile delivery, or AI tutoring behavior
- Redesigning the full learner UX beyond the states needed for governed availability clarity

## Decisions

### 1. `lesson_governance.py` will own learner-delivery resolution

The platform will treat `lesson_governance.py` as the canonical policy module for:
- approved-ready determination
- learner-visible lesson selection
- direct learner lesson eligibility
- governed progression eligibility
- audience-aware lesson serialization
- institution-safe unavailable outcomes

Rationale:
- The repository already uses this module as the strongest existing source of governance logic.
- Hardening an existing policy module is safer than spreading rules into routes or creating a parallel orchestration layer.

Alternative considered:
- Keep per-route governance decisions with small helper reuse.
- Rejected because current drift came from that pattern.

### 2. Learner-facing routes will consume governed selections, not raw lessons

Learner-facing course payloads, direct lesson fetches, start-course flows, and progress creation will all resolve their lesson sets from the same governed lesson-selection function. Raw unit lesson lists will remain available for educator and review contexts only.

Rationale:
- Institutional trust depends on progress matching what learners are actually allowed to see.
- This removes the current mismatch where learner-visible course data and learner-driven progress can diverge.

Alternative considered:
- Allow progress creation from all lessons while hiding draft lessons in course payloads.
- Rejected because that preserves non-auditable learner progression.

### 3. No learner fallback-to-draft behavior will remain

When a learner requests content and no approved-ready governed path exists, the system will return an explicit unavailable outcome rather than returning the requested draft lesson or substituting an arbitrary sibling lesson.

Rationale:
- Silent substitution weakens determinism.
- Silent draft delivery weakens governance integrity.
- Explicit unavailable states are safer for institutions and easier to test.

Alternative considered:
- Preserve sibling substitution when a governed lesson exists.
- Rejected because it makes lesson identity and progression semantics ambiguous.

### 4. Educator visibility remains broader than learner visibility

Educators, reviewers, and authors will continue to access in-progress lesson content, governance metadata, and staff-only instructional fields. However, those audience distinctions will be driven by centralized serialization and delivery rules rather than ad hoc route branching.

Rationale:
- The platform must preserve authoring and review productivity.
- Centralized audience handling reduces route-level drift and payload inconsistency.

Alternative considered:
- Split learner and educator APIs into entirely separate systems.
- Rejected because the current architecture can support both through clearer policy boundaries.

### 5. Demo seed data must model governed production behavior

Demo and seeded learner environments will include:
- deterministic unit ordering
- deterministic lesson ordering
- approved-ready learner-visible lessons
- governed progression paths that match production rules

Rationale:
- Demo reliability is part of operational trust.
- Seed data that bypasses governance makes regressions harder to detect and misrepresents platform readiness.

Alternative considered:
- Keep lightweight seed data and rely on separate test fixtures for governed delivery.
- Rejected because demo environments are already part of product validation and regression confidence.

## Risks / Trade-offs

- [Risk] Existing tests or UI flows may implicitly rely on fallback-to-draft behavior -> Mitigation: introduce explicit unavailable-state contracts and update tests around the new learner-safe behavior
- [Risk] Historical progress rows may already reference lessons that are no longer governed-deliverable -> Mitigation: define migration-safe continuation behavior and add guardrails around resumed learner delivery
- [Risk] Centralizing learner-delivery policy in one module can create a large responsibility surface -> Mitigation: keep policy functions narrowly named and separate eligibility, selection, serialization, and availability responsibilities within the same module
- [Risk] Demo seeding becomes slightly heavier -> Mitigation: keep the seed minimal in volume but fully governed in quality and ordering
- [Risk] Educator expectations may shift if current hidden route shortcuts disappear -> Mitigation: preserve broader educator visibility explicitly and document audience-specific delivery behavior in specs

## Migration Plan

1. Introduce canonical governed-selection and unavailable-state helpers in `lesson_governance.py`
2. Refactor learner-facing routes to consume those helpers without changing the underlying lesson, course, or progress models
3. Align start-course and progress creation flows to governed lesson eligibility
4. Update demo seed data so learner-visible demo paths are approved-ready and ordered deterministically
5. Add integration tests that exercise governed learner behavior across all affected routes
6. Roll out with verification against existing educator flows to confirm broader authoring visibility remains intact

Rollback strategy:
- Because this is an evolutionary hardening change, rollback can restore prior route behavior if a release issue emerges
- No destructive schema replacement is required for the core design

## Open Questions

- How should the platform surface resumed progress when a previously governed lesson becomes unavailable after progress already exists?
- Should learner-unavailable states return a standardized API error contract, a structured unavailable payload, or both depending on endpoint type?
- Which instructional fields beyond `teacher_notes` and `discussion_questions` should be formally classified as learner-visible versus educator-only as the curriculum model matures?
