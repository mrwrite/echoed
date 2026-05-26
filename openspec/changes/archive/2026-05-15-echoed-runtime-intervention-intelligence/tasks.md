## 1. Recommendation Semantics

- [x] 1.1 Define bounded runtime intervention recommendation structures and deterministic state semantics for reteach, review, enrichment, monitor, and normal continuation.
- [x] 1.2 Reuse existing governed runtime support and educator visibility read paths to derive recommendation outputs without introducing a parallel intervention engine.
- [x] 1.3 Attach bounded evidence-basis and confidence/caution fields to recommendation outputs using existing governed evidence only.

## 2. Integrity Guardrails

- [x] 2.1 Integrate competency evidence integrity and mastery safety helpers into runtime intervention recommendation derivation.
- [x] 2.2 Exclude or downgrade unsafe deprecated, archived, superseded, or ambiguous evidence from recommendation authority while preserving historical evidence anchoring.
- [x] 2.3 Verify runtime intervention intelligence remains read-only and does not mutate learner progression, attempts, mastery, certification, reporting, or governed delivery state.

## 3. Educator Visibility

- [x] 3.1 Expose runtime intervention intelligence through existing authorized educator/staff visibility surfaces as read-only guidance only.
- [x] 3.2 Preserve learner-safe and non-predictive recommendation tone without introducing assignment, messaging, grading, publish, rollback, or edit actions.
- [x] 3.3 Preserve existing auth/session boundaries, route structure, premium UX primitives, and learner continuation determinism.

## 4. Verification

- [x] 4.1 Add focused regression coverage for reteach, review, enrichment, monitor, and normal recommendation paths.
- [x] 4.2 Add focused regression coverage for evidence basis, caution flags, and historically unsafe or ambiguous evidence handling.
- [x] 4.3 Verify no progression, scoring, certification, or reporting mutation is introduced and existing governed delivery behavior remains unchanged.

## Follow-Ups

- [ ] Add batching or combined governance payload for staff course read models
- [ ] Refactor private analytics helper dependencies into a shared read-model service
- [ ] Decide whether course-wide competency ambiguity should downgrade all learners or only affected learners
- [ ] Improve frontend wording normalization for backend recommendation/caution messages
- [ ] Clean up Windows encoding artifacts in staff dashboard templates
- [ ] Clean up noisy student-view error-path console logs
- [ ] Address pre-existing Pydantic config and datetime.utcnow() warnings