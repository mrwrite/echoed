# Studio Lesson Data Contract

Date: 2026-07-13

## Existing lesson model

The current lesson response can include: `id`, `title`, `objective`, `learning_objectives`, `key_concepts`, `teacher_notes`, `discussion_questions`, `hook`, `content`, `guided_practice`, `independent_practice`, `assessment`, `review_status`, `reviewed_by`, `order`, `duration_minutes`, sources, activities, readiness fields, revision metadata, and timestamps.

Activities include `id`, `type`, `title`, `content`, `order`, and storybook pages. Lesson sources include `id`, `citation`, optional URL, and timestamp.

## Authorization

`GET /api/lessons/{id}` accepts admin, teacher, and student. Lesson list/create/update/delete accept admin and/or teacher. They do not authorize `content_admin`. The nested legacy course editor also uses admin/teacher mutations.

## Studio behavior

- Canonical Studio does not expose a false lesson editor.
- `lesson_draft` artifacts are labeled **Content drafts**, not learner lessons.
- Draft preview uses only artifact content and never calls start-course, lesson-session, enrollment, or progress APIs.
- Teacher-only versus learner-visible fields are not presented as editable until an authorized response/mutation contract exists.
- Technical identifiers are omitted from visible draft relationships.

## Verified gap

Content administrators need organization-scoped lesson read/write APIs, ownership checks, a stable content model, source association, activity/assessment association, save-failure recovery, and a preview response that cannot create runtime state. The existing endpoints do not satisfy that workflow.
