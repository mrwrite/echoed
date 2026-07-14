# Studio Program and Learning-Path Data Contract

Date: 2026-07-13

## Verified models

The legacy `Program` model exposes `id`, `title`, `description`, `organization_id`, `created_by`, timestamps, and ordered `ProgramCourse` links containing `course_id`, `order`, and `is_required`. `GET /api/programs` and detail are authenticated reads; `POST /api/programs` is restricted to `admin` and `teacher`. No update, delete, membership-edit, or reorder endpoint is present.

The V2 `Product` wrapper can carry `program_id` or use `product_type: learning_path`. Content administrators can create, review, and publish these organization-scoped wrappers through V2 endpoints. A wrapper does not create or modify a legacy Program.

## Studio behavior

- `/studio/programs` lists program-backed and `learning_path` wrappers.
- It shows title, description, wrapper status, review state, and visibility.
- Course membership, ordering, learner progress, and enrollment are not editable.
- Creation through `/studio/create` creates a wrapper only and states that consequence.
- No delete or reorder control is shown.

## Visibility and availability

V2 visibility supports `draft`, `private`, `workspace`, `invite_only`, `public`, and `archived`. Wrapper publishing can make the public page visible but does not enroll learners or create a program runtime. Existing enrollment and access-grant behavior remains authoritative.

## Gap

A complete content-admin program editor requires organization-scoped program reads plus create/update/course-membership/reorder/archive APIs with ownership validation. Until then, Studio presents supported wrapper governance only.
