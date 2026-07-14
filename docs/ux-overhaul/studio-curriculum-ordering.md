# Studio Curriculum Ordering

Date: 2026-07-13

## Verified ordering fields

- `ProgramCourse.order` orders courses in a program.
- `Unit.order` orders units.
- `Lesson.order` orders lessons.
- `Activity.order` and `StorybookPage.order` order lesson content.

## API and role boundary

Legacy unit, lesson, activity, and program creation APIs are restricted to `admin` or `teacher`; the program API has no update/reorder endpoint. Course-version unit APIs also exclude `content_admin`. The V2 wrapper APIs do not expose curriculum ordering.

## Production behavior

Canonical Studio preserves backend ordering when records are returned, but does not expose drag-and-drop, move controls, or optimistic ordering. No order is persisted from the frontend because no complete authorized API exists.

## Failure recovery requirement for future work

Any future reorder contract must accept explicit ordered identifiers, validate organization/content ownership, return the confirmed order, preserve the previous order after failure, announce success/failure, and provide keyboard move controls. Drag-and-drop may only be an enhancement to those controls.
