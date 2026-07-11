# Student Course Navigation

Date: 2026-07-11

## Decision

The canonical student course overview route is:

`/learn/courses/:courseId`

A dedicated unit route was not added in this phase. The course overview renders unit sections inline through `StudentCurriculumComponent`.

## Rationale

- The current backend supports `GET /api/courses/{course_id}` with ordered units and lessons.
- The current student progress API exposes the current governed segment, not independent unit-level navigation, per-unit completion, or unit deep-link authorization.
- Adding `/learn/courses/:courseId/units/:unitId` now would duplicate the course hierarchy without a stronger backend contract for unit progress or availability.
- Inline unit sections preserve browser back behavior, keep the primary action clear, and avoid implying unsupported direct lesson navigation.

## Navigation Rules

- `/learn` remains the student canonical home.
- `/learn/products` remains a transitional course browsing page backed by the learner-product API.
- `/learn/courses/:courseId` is the canonical course path and can be deep linked.
- `/learn/lesson/:id` remains the governed runtime route where `:id` is a student unit progress id, not a course or lesson id.
- Student lesson rows do not navigate directly unless they represent the current governed segment.
- Non-current lessons communicate their state as included/locked/unavailable using text, not color alone.

## Future Unit Route Criteria

Add `/learn/courses/:courseId/units/:unitId` only after the API can safely provide:

- student unit progress summary,
- current lesson for that unit,
- locked/unlocked lesson state per lesson,
- direct-link guard semantics for inaccessible units,
- back/next behavior that does not bypass `startCourse()`.
