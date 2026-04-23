# Tasks

## 1. Lesson Structure Alignment

- [ ] Audit existing lessons to ensure they support:
  - learning_objectives
  - key_concepts
  - hook
  - content
  - guided_practice
  - independent_practice
  - assessment
- [x] Ensure lesson schemas and responses consistently expose these fields
- [x] Ensure lesson viewer renders instructional sections in the correct order

---

## 2. Source Integration

- [ ] Verify all lessons support at least one linked source
- [x] Ensure source data (citation, URL) is consistently returned from APIs
- [x] Ensure sources are rendered clearly at the bottom of lessons
- [x] Validate that source handling aligns with existing lesson governance rules

---

## 3. Instructional Flow Consistency

- [x] Ensure lessons follow the defined instructional sequence:
  - hook → content → guided → independent → assessment
- [x] Ensure frontend rendering reflects this sequence consistently
- [x] Ensure no sections break existing lesson or activity flows

---

## 4. Educator Guidance Layer

- [x] Verify teacher_notes and discussion_questions exist and are usable
- [x] Ensure teacher-only fields remain hidden from students
- [x] Ensure teacher-facing views expose instructional guidance clearly

---

## 5. API and Model Consistency

- [x] Ensure lesson and course APIs return academic-quality fields consistently
- [x] Ensure no duplicate lesson or source models were introduced
- [x] Ensure alignment with lesson_governance.py for readiness and visibility behavior

---

## 6. Frontend Alignment

- [x] Ensure Angular lesson model supports all academic-quality fields
- [x] Ensure lesson viewer UI remains clean for students
- [x] Ensure no layout or rendering regressions occur

---

## 7. Verification

- [x] Run targeted backend tests related to lessons and governance
- [x] Run TypeScript compilation checks
- [x] Run frontend tests for lesson viewer behavior
- [ ] Validate manual lesson flow for both student and teacher roles
