# Teacher Privacy Review

Date: 2026-07-12

## Decisions

- Canonical learner detail requires `sectionId` and verifies the learner appears in that section roster before showing profile context.
- Roster rows show learner name only when the authorized student list includes that profile.
- Emails, internal organization IDs, raw learner IDs, demographic data, and global learner search are not shown in teacher UI.
- Deep-link learner failures use neutral permission language and do not reveal whether a learner exists outside the teacher's authorized class context.
- Course preview does not call `startCourse()` and does not create teacher enrollment, learner enrollment, lesson sessions, or progress records.
- Unsupported discussion moderation is not exposed because thread/post APIs are not class-scoped or permission-scoped.

## Remaining Backend Privacy Gaps

- Section roster/enrollment/assignment APIs should verify the target section belongs to the active organization and the educator's authorized scope.
- Assignment listing should require an educator or authorized learner dependency.
- Thread/post APIs should require authentication and class/community scope before Teach moderation is exposed.
