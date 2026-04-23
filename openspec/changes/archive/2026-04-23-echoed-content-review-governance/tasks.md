## 1. Backend Governance Rules

- [x] 1.1 Add shared lesson-governance helpers for readiness evaluation, source validation, review permission checks, and audience-aware lesson visibility using the existing `Lesson` and `Source` models
- [x] 1.2 Update `backend/app/api/routes/lessons.py` to enforce reviewer-controlled `review_status` transitions, system-managed `reviewed_by`, and readiness checks before `reviewed` or `approved` states are accepted
- [x] 1.3 Update `backend/app/schemas.py` and any lesson request/response contracts needed so governance validation details and role-filtered lesson fields can be represented without introducing duplicate lesson models

## 2. Lesson And Course API Enforcement

- [x] 2.1 Update lesson read paths to prefer approved and academically ready lessons for students while allowing deterministic fallback when no approved lesson exists
- [x] 2.2 Update course serialization in `backend/app/api/routes/courses.py` so student-facing nested lesson payloads exclude unapproved or not-ready lessons while teacher/admin responses continue to include all lessons
- [x] 2.3 Ensure student-facing lesson payloads suppress `teacher_notes` and `discussion_questions` while preserving existing lesson/activity delivery behavior

## 3. Frontend Visibility Updates

- [x] 3.1 Update the Angular lesson model and any consuming services to handle governance-filtered lesson payloads without breaking current lesson delivery flows
- [x] 3.2 Update `frontend/src/app/shared/lesson-viewer.component.*` to hide teacher notes and discussion questions in learner mode and gracefully handle lessons filtered by approval/readiness status

## 4. Verification

- [x] 4.1 Add backend tests for readiness failures, valid review transitions, unauthorized review-field updates, and student filtering in direct lesson APIs
- [x] 4.2 Add backend tests for course API visibility so students only receive approved, ready nested lessons and staff still receive full authoring views
- [x] 4.3 Add frontend tests or component coverage for learner gating of teacher notes and discussion questions, then run targeted backend and frontend verification for the governance workflow

## 5. Final Review Checks

- [x] Editing an approved lesson has defined behavior (either remains approved for minor edits or reverts to draft for material changes)
- [x] Student payload fallback is deterministic when no approved-ready lesson exists
- [x] Student payload fallback still hides:
  - [x] teacher_notes
  - [x] discussion_questions
- [x] `lesson_governance.py` is the single source of truth for:
  - [x] readiness rules
  - [x] reviewer-capable logic
  - [x] student/teacher visibility rules
- [x] Student, teacher, and reviewer/admin behavior is consistent between:
  - [x] `lessons.py`
  - [x] `courses.py`
- [x] `reviewed_by` is never accepted directly from client payloads

## Future Follow-Up

- [ ] Consider adding patch-style lesson editing or explicit review-preserving edit behavior so approved lessons are not unintentionally demoted by clients that omit `review_status`
