## Why

EchoEd already has lesson governance, readiness checks, audience-aware serialization, course delivery, and learner progress tracking, but those behaviors are not yet fully aligned into one deterministic learner-delivery contract. The current platform can still drift between course payloads, direct lesson fetches, start-course behavior, progress creation, and demo delivery in ways that weaken academic trust.

This change is needed now because institutional expansion depends on governed learner delivery being authoritative, repeatable, and auditable. Learner progression must only be driven by lessons that are actually approved and ready, and the platform must stop using convenience fallbacks that blur draft content, governed content, and production learner experience.

## What Changes

- Define one canonical governed lesson-selection flow for learner delivery and make it the authoritative path across `lessons.py`, `courses.py`, `start_course.py`, and progress-related flows
- Ensure learner progress rows are created only for learner-visible governed lessons and that governed lesson selection drives segment, unit, and course progression deterministically
- Replace silent fallback-to-draft behavior with explicit institution-safe unavailable or pending-review delivery outcomes
- Preserve educator, reviewer, and author visibility while keeping learner payloads strictly governance-filtered and audience-aware
- Make `lesson_governance.py` the canonical source for approved-ready determination, learner visibility, governed fallback behavior, progression eligibility, and audience-aware lesson delivery
- Harden demo and seed behavior so demo learners always receive approved-ready lessons with deterministic ordering and valid governed progression paths
- Add verification coverage for governed course delivery, governed lesson fetch, governed start-course behavior, governed progress creation, unavailable states, and demo learner visibility
- Preserve the current EchoEd lesson, course, unit, governance, and progress architecture rather than introducing parallel delivery or lesson systems

## Capabilities

### New Capabilities
- `governed-learner-delivery`: Defines the canonical governed lesson-selection contract for learner-visible lesson delivery across all learner-facing flows
- `governed-progression-integrity`: Defines how governed lesson selection drives progress creation, continuation, and persistence without draft or unapproved lesson drift
- `unavailable-lesson-delivery-states`: Defines institution-safe behavior when a learner-visible approved-ready lesson path does not exist
- `demo-governed-learning-reliability`: Defines production-aligned demo and seed guarantees for governed lessons, ordering, and learner progression

### Modified Capabilities
- `lesson-delivery-and-activity-system`: Tighten learner delivery requirements so governed lesson selection and progression eligibility are enforced end to end
- `course-and-lesson-api-contracts`: Update learner-facing course and lesson API behavior to remove ambiguous fallback delivery and require explicit governed outcomes
- `role-based-content-visibility`: Clarify centralized audience-aware serialization expectations for learner, educator, reviewer, and author contexts

## Impact

- Backend:
  - `lesson_governance.py` becomes the canonical policy layer for learner delivery eligibility and governed progression inputs
  - `courses.py`, `lessons.py`, `start_course.py`, and progress flows must align to the same governed lesson-resolution behavior
  - Seed and demo flows must create production-representative governed learner paths

- Frontend:
  - Learner lesson experiences must surface explicit unavailable or pending-review states instead of ambiguous fallbacks
  - Educator experiences may continue exposing in-progress governed content, but must do so through audience-aware payloads

- Testing:
  - Integration coverage must verify deterministic governed behavior across lesson fetch, course delivery, start-course flows, progress creation, and demo environments

- Strategic Alignment:
  - This initiative directly supports `echoed-platform-foundation-hardening`
  - This initiative directly supports `echoed-academic-quality-foundation`
  - This initiative directly supports the archived governance behavior represented by `lesson-delivery-and-activity-system`, `course-and-lesson-api-contracts`, `content-review-workflow`, `lesson-readiness-validation`, and `role-based-content-visibility`
  - This initiative directly supports `echoed-global-education-platform-evaluation`
