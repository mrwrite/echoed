## 1. Canonical Governed Delivery

- [x] 1.1 Audit existing learner-facing lesson resolution across `lessons.py`, `courses.py`, `start_course.py`, and progress-related flows against the new governed-delivery specs
- [x] 1.2 Define canonical governance-layer helpers for learner lesson eligibility, governed lesson selection, and learner-unavailable outcomes in `lesson_governance.py`
- [x] 1.3 Refactor learner-facing course delivery to consume only canonical governed lesson-selection behavior
- [x] 1.4 Refactor learner-facing direct lesson delivery to consume the same canonical governed lesson-selection behavior without sibling or draft fallback drift

## 2. Governed Progress Integrity

- [x] 2.1 Refactor start-course initialization so segment progress rows are created only for governed learner-visible lessons
- [x] 2.2 Align segment advancement and continuation flows to the governed learner-visible lesson sequence
- [x] 2.3 Define and implement institution-safe behavior for learner continuation when no governed next lesson exists
- [x] 2.4 Verify that governed learner delivery and stored progress remain auditable and consistent across unit and course completion flows

## 3. Audience-Aware Delivery Separation

- [x] 3.1 Centralize learner versus educator serialization decisions so route modules do not diverge on staff-only versus learner-visible fields
- [x] 3.2 Preserve educator, reviewer, and author visibility for in-progress content while keeping learner payloads strictly governed
- [x] 3.3 Define learner-facing unavailable or pending-review UX states for governed delivery failures without exposing draft-state ambiguity

## 4. Demo & Seed Hardening

- [x] 4.1 Update demo seed data to include deterministic ordered governed units and approved-ready learner-visible lessons
- [x] 4.2 Ensure seeded learner progression paths exercise the same governed production behavior as normal learner delivery
- [x] 4.3 Deferred: add verification that demo/student environments fail loudly when seeded content is no longer governed-deliverable. Tracked under Follow-Ups.

## 5. Verification & Regression Coverage

- [x] 5.1 Add backend integration coverage for governed course delivery, governed lesson fetch, and explicit unavailable learner outcomes
- [x] 5.2 Add backend integration coverage for governed start-course behavior and governed progress-row creation
- [x] 5.3 Add coverage for continuation and completion behavior when governed next lessons are unavailable
- [x] 5.4 Add seed and demo verification coverage for governed learner visibility and deterministic ordering
- [x] 5.5 Deferred: add targeted frontend coverage for learner unavailable states and governed learner-mode clarity where contracts change. Tracked under Follow-Ups.

## Follow-Ups

- [ ] Add cleanup/audit tooling for historical `SegmentProgress` rows tied to non-governed lessons
- [ ] Review whether `get_student_courses` should continue creating governed progress state during read paths or move that behavior to an explicit command endpoint
- [ ] Add frontend regression tests for governed unavailable-state rendering
- [ ] Add a demo failure-mode test that intentionally breaks governed seed content and verifies the failure is detected