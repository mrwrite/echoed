# Student Course Data Contract

Date: 2026-07-11

## Summary

The completed student Phase 2 course overview composes existing frontend services and backend endpoints. No backend endpoint, database schema, role model, or progress rule was changed.

| Field | Frontend source | Backend endpoint/schema | Returned | Derived | Optional | Safe to display | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Course identifier | `Course.id`, `StudentCourseWithDetails.course_id` | `GET /api/courses/{course_id}` -> `CourseResponse.id`; `GET /api/student-courses` -> `StudentCourseWithDetails.course_id` | Yes | No | No | Yes | Used by canonical `/learn/courses/:courseId`. |
| Course title | `Course.title` | `CourseResponse.title` | Yes | No | No | Yes | Primary page title. |
| Course description | `Course.description` | `CourseResponse.description` | Yes | No | Yes in frontend model | Yes | Hidden if missing; no generated objectives. |
| Course image | `CourseDraft.imageUrl`, legacy card fields | Not included in `CourseResponse` | No | No | Yes | Not used | Existing API gap; overview uses content-first layout. |
| Enrollment/access state | `StudentCourseWithDetails` match by `course_id` | `GET /api/student-courses` | Yes for enrolled courses | No | Yes | Yes | Not enrolled courses are startable only through existing enroll flow. |
| Start state | `startCourse()` response | `POST /api/start-course` -> `SegmentResponse` | Yes | No | Yes | Yes | Backend requires enrollment and governs availability. |
| Completion state | `StudentCourseWithDetails.status` | `StudentCourseWithDetails.status` | Yes | No | Yes | Yes | Completed courses show review-only action. |
| Unit list/order | `course.units[].order` | `CourseResponse.units` / `UnitResponse.order` | Yes | Sorted client-side by returned order | Yes | Yes | No separate unit progress endpoint is used for students. |
| Lesson list/order | `unit.lessons[].order` | `LessonResponse.order` | Yes | Sorted client-side by returned order | Yes | Yes | Frontend `Lesson` model now includes `order?: number`. |
| Locked/unlocked state | Current `SegmentResponse` | `GET /api/progress/segment` | Only current segment state | Partially | Yes | Yes with caveats | Only current governed lesson is openable; other lessons are labeled locked/unavailable without bypassing governance. |
| Current lesson | `SegmentResponse.lesson_id` | `SegmentResponse.lesson_id` | Yes | No | Yes | Yes | Used for current lesson state and course runtime context. |
| Current unit | Course hierarchy containing current `lesson_id` | `CourseResponse.units[].lessons[]` | No direct field | Yes | Yes | Yes | Derived only to display location, not to authorize navigation. |
| Course progress | `CoursesService.getCourseProgress()` | Composes `GET /api/progress/segment` | No direct percentage in backend response | Yes | Yes | Yes | Existing frontend behavior preserved. |
| Unit progress | Current unit marker plus completed-course status | No student unit progress summary endpoint | No | Limited | Yes | Yes with neutral labels | Labels are "Current unit", "Included in course", or completed-course counts. |
| Lesson progress | Current segment only | `SegmentResponse.status`, `delivery_state` | Partial | Limited | Yes | Yes with neutral labels | No per-lesson completion matrix is available. |
| Assignment context | Not currently consumed by student course overview | Assignment APIs exist separately | Not in student course response | No | Yes | Not shown | Avoids fabricated assignment behavior. |
| Program/path context | `ProgramsService` surfaces paths separately | `/api/programs` | Not in course response | No | Yes | Not shown on course overview | Future phase can connect program context if API supports it. |
| Badge outcome | Badge/cert preview on `/learn`; certificates page | Badge and certification APIs | Partial | No | Yes | Yes | Course overview links to Achievements without promising a specific badge. |
| Certification outcome | `ProgramsService.getMyCertifications()` | `/api/students/me/certifications` | Yes for earned certs | No | Yes | Yes | No download/print action is fabricated. |
| Prerequisites | None found in student API | N/A | No | No | Yes | Not shown | Backend gap if future UX requires prerequisite display. |
| Required vs optional lessons | Not returned in course hierarchy | N/A | No | No | Yes | Not shown | Avoided to prevent unsupported claims. |

## Known Gaps

- `CourseResponse` does not return a course image.
- Student APIs do not return a complete per-lesson state matrix for locked, completed, available, retry, or required/optional status.
- Unit progress is not returned as a student-facing summary.
- Program/path context is separate from the course response and is not joined into the overview in this phase.
