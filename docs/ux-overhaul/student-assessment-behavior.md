# Student Assessment Behavior

Date: 2026-07-11

## Current API Behavior

- Assessments load through `ProgramsService.getAssessment(id)` -> `GET /api/assessments/{assessment_id}`.
- Assessment attempts submit through `ProgramsService.submitAssessment(id, answers)` -> `POST /api/assessments/{assessment_id}/attempts`.
- Availability is governed by `is_available_for_learner`, `learner_delivery_state`, and `learner_delivery_detail`.
- The frontend requires every question to have an answer before submission.
- Submission returns score, max score, percentage, passed, submitted timestamp, and per-answer correctness/points.
- If an assessment belongs to a program, existing certification evaluation is refreshed with `GET /api/certifications?program_id=...` and `POST /api/certifications/{id}/evaluate`.

## Implemented UX Rules

- Unavailable assessments hide the form and show a shared unavailable/blocked state.
- Learners see answer count before submission.
- Final submission uses `EchoConfirmationDialogComponent`.
- The confirmation explains that answers will be submitted for scoring and that this screen does not expose editing after submission.
- Submission loading uses the shared loading state and sets `aria-busy` on the form.
- Submission failure preserves answers, keeps the confirmation dialog open, and shows the failure message.
- Results use learner-centered language: `Passed`, `Needs more practice`, `Confirmed understanding`, and `Review this idea`.
- The page links to `/learn/paths` and `/learn/certificates`; legacy `/home` links were removed from visible student copy.

## Not Changed

- No grading policy changed.
- No retry policy changed.
- Correct answers are not newly revealed.
- No new assessment sessions or incremental save behavior were introduced.
- No backend endpoints were added.

## Known Gaps

- The API does not currently expose whether retry is available after a failed attempt.
- Teacher-review-required state is not clearly surfaced beyond generic availability fields.
- Question-by-question review is limited to the result data currently returned by the backend.
