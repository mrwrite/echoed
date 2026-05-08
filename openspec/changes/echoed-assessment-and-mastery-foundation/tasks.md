## 1. Assessment domain foundation

- [ ] 1.1 Define the canonical assessment taxonomy, scope model, lifecycle states, and attempt history records.
- [ ] 1.2 Add persistence and service boundaries for authoritative assessment attempts, review events, grading events, and evidence metadata.
- [x] 1.3 Wire assessment records to the existing course/unit/lesson/activity hierarchy without introducing a parallel content tree.

## 2. Learner assessment delivery

- [ ] 2.1 Implement governed learner assessment resolution for lesson, unit, course, and mastery-check contexts.
- [ ] 2.2 Add explicit unavailable assessment states for locked, expired, unpublished, or unauthorized assessments.
- [ ] 2.3 Preserve governed attempt lifecycle and feedback visibility rules for learner-facing assessment views.

## 3. Educator assessment operations

- [ ] 3.1 Implement educator assignment workflows for cohort, section, lesson, unit, and course assessment scopes.
- [ ] 3.2 Add manual grading and rubric-driven review flows that append to authoritative attempt history.
- [ ] 3.3 Surface intervention and pacing signals for educators based on mastery and attempt outcomes.

## 4. Mastery and progression integration

- [x] 4.1 Define mastery thresholds and competency/objective alignment rules.
- [x] 4.2 Aggregate mastery deterministically from lesson evidence to unit and course readiness.
- [ ] 4.3 Connect mastery outcomes to the existing governed progression authority and remediation triggers.

## 5. Reporting, evidence, and integrity

- [x] 5.1 Build evidence-backed gradebook and reporting read models from canonical assessment records.
- [x] 5.2 Add learner evidence history and institutional audit outputs for grading and mastery records.
- [ ] 5.3 Ensure grading overrides, feedback release, and attempt updates remain auditable and append-only.

## 6. Verification and rollout

- [ ] 6.1 Add tests for canonical assessment taxonomy, lifecycle, retake policy, and unavailable states.
- [ ] 6.2 Add tests for mastery aggregation, progression eligibility, and intervention handling.
- [ ] 6.3 Add tests for educator review, rubric grading, audit history, and reporting consistency.
- [ ] 6.4 Validate that no new parallel grading or progression system is introduced during implementation.
