## 1. UI shell polish

- [x] 1.1 Audit the authenticated shell, header, and sidebar across student and teacher entry flows for layout shift, unstable first paint, and broken responsive behavior
- [x] 1.2 Normalize role-aware shell bootstrap so header, sidebar, and primary dashboard content render only from resolved authenticated context
- [x] 1.3 Fix pilot-critical shell polish defects in shared navigation, spacing, and return-path behavior without introducing a parallel shell system

## 2. Student dashboard polish

- [x] 2.1 Audit the current student dashboard continuation path, active course card, and available-course surfaces against pilot readiness expectations
- [x] 2.2 Harden continuation, empty, and retry behavior so students can reliably understand their next governed learning step
- [x] 2.3 Verify the student can log in, see the active course, enter the lesson, and return safely without contradictory dashboard state

## 3. Lesson runtime polish

- [ ] 3.1 Audit the lesson runtime entry, governed blocked state, error recovery, and exit-to-dashboard behavior for readability and continuity
- [ ] 3.2 Harden lesson runtime state rendering so loading, blocked, error, and completed outcomes remain distinct and user-friendly
- [ ] 3.3 Verify the lesson runtime preserves governed delivery semantics and safe navigation across refresh and return flows

## 4. Teacher dashboard baseline polish

- [ ] 4.1 Audit the current teacher dashboard for pilot-demo readiness, focusing on course visibility, learner progress context, runtime support visibility, and responsive usability
- [ ] 4.2 Harden teacher dashboard loading, empty, and retry behavior so the core pilot narrative remains usable even when some datasets are unavailable
- [ ] 4.3 Verify a teacher can log in and see enough stable dashboard state to demonstrate course, learner, and runtime context

## 5. Error/loading/empty states

- [ ] 5.1 Inventory route-local loading, error, blocked, and empty states across shell, student dashboard, teacher dashboard, and lesson runtime
- [ ] 5.2 Align pilot-critical flows to the canonical UX state system and remove ambiguous placeholders where stale content remains visible
- [ ] 5.3 Add or update tests that lock in the intended user-friendly state behavior where practical

## 6. Accessibility pass

- [ ] 6.1 Review pilot-critical student, teacher, shell, and lesson surfaces for contrast, focus visibility, keyboard order, and labeling defects
- [ ] 6.2 Fix obvious unreadable text, weak contrast, and missing actionable semantics in core pilot flows
- [ ] 6.3 Document any remaining accessibility limitations that are intentionally deferred beyond Phase 1

## 7. Backend runtime verification

- [ ] 7.1 Audit progression and runtime routes that govern course start, lesson continuation, segment completion, and governed blocked behavior
- [ ] 7.2 Fix or reinforce any targeted progression/runtime defects while preserving real auth and governed delivery rules
- [ ] 7.3 Extend or refresh backend pytest coverage for governed progression safety, non-governed progression continuity, and deterministic demo seed behavior

## 8. Smoke tests / docs

- [ ] 8.1 Review existing demo seed, smoke validation, and pilot-readiness documentation for drift against current student and teacher flows
- [ ] 8.2 Update bounded smoke and manual verification docs so a pilot operator can prepare the demo environment and validate core student/teacher flows deterministically
- [ ] 8.3 Verify the existing student Playwright smoke remains green and document any intentionally manual teacher checks

## 9. Final validation

- [ ] 9.1 Run the full backend pytest suite and confirm it remains green
- [ ] 9.2 Run the existing Angular test suite and confirm it remains green
- [ ] 9.3 Run the existing student Playwright smoke and confirm the pilot-critical student path remains green
- [ ] 9.4 Confirm no production auth was weakened, demo seed remains deterministic, and new Phase 1 behavior is covered by tests or documented manual verification
