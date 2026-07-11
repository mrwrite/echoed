# Student Session Recovery

Date: 2026-07-11

## Current Recovery Rules

- `/learn/lesson/:id` and legacy `/home/lesson/:id` both use `LessonViewComponent`.
- On lesson route load, the component calls `CoursesService.getCurrentSegment(unitProgressId)`.
- If the segment is `governed_available` and includes `lesson_id`, the component loads the lesson with `CoursesService.getLessonById(lesson_id)`.
- If the segment is unavailable, pending review, empty, or completed, the component renders a student-safe state instead of exposing raw IDs.
- If `getCurrentSegment()` returns 404, the component calls `CoursesService.getStudentCourses()` and looks for an active course with `unit_progress_id`.
- If an active replacement segment is found, it navigates to the recovered `unit_progress_id` and reloads the governed segment.
- If recovery fails, the component renders a retryable error state.
- Lesson completion calls `CoursesService.markSegmentCompleted()` and only advances or completes after the API succeeds.
- Completion failure leaves the lesson open and shows: "We could not save this lesson completion. Your lesson is still open, so try again before leaving."

## Implemented In This Phase

- Canonical exit and completion return now use `/learn`.
- Completion save state uses `role="status"` with polite live announcement.
- Completion failure uses `role="alert"` and does not close the lesson.
- Duplicate completion calls are blocked while a completion request is in progress.

## Deferred

- Local temporary draft preservation for unsent activity responses.
- Leave-with-unsaved-work confirmation tied to activity inputs.
- Dedicated session-expired panel that differentiates auth expiry from temporary API failure.
