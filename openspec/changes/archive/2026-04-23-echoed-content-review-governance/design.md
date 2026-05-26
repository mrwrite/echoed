## Context

EchoEd already extended the existing `Lesson` model with academic-quality fields and linked lesson sources. That work added content structure (`learning_objectives`, `key_concepts`, `hook`, `content`, `guided_practice`, `independent_practice`, `assessment`), teacher-facing metadata (`teacher_notes`, `discussion_questions`), and review metadata (`review_status`, `reviewed_by`) directly onto the current lesson system. The existing lesson routes in `backend/app/api/routes/lessons.py` and nested course serialization in `backend/app/api/routes/courses.py` now expose those fields without any governance rules beyond validating that `review_status` is one of `draft`, `reviewed`, or `approved`.

This leaves three gaps:

1. Academic completeness is not enforced before a lesson is treated as approved content.
2. Review fields can currently be set by any caller that can update a lesson.
3. Student-facing APIs and the Angular lesson viewer currently receive the same lesson payload as authoring users, including teacher-only fields and unapproved content.

The design must preserve the existing Course -> Unit -> Lesson structure, reuse the current progress and lesson delivery flows, and avoid introducing a separate publishing or review subsystem.

## Goals / Non-Goals

**Goals:**
- Define a single readiness rule set for academically complete lessons using the existing lesson and source fields.
- Enforce readiness and role checks when lessons move into reviewed or approved states.
- Restrict who can update `review_status` and `reviewed_by` without changing how normal lesson content is edited.
- Keep lesson and course APIs compatible while making student-facing responses consistent for draft and unapproved lessons.
- Gate teacher-only lesson content in the frontend using the existing lesson viewer and route structure.
- Add targeted tests for readiness validation, review permissions, and visibility behavior.

**Non-Goals:**
- Creating a new lesson workflow model, moderation queue, or separate review table.
- Rewriting the current auth, organization, course, or progress systems.
- Introducing a new publishing pipeline for courses or versions beyond lesson-level governance.
- Reworking student progress semantics or activity completion behavior.
- Building a new authoring UI; this change only adds minimal visibility and governance logic.

## Decisions

### 1. Readiness will be computed from existing lesson data, not stored as a new persisted state

The backend will add a shared readiness evaluator that inspects the existing `Lesson` and `Source` fields and returns:
- whether the lesson is academically complete
- which required elements are missing

The evaluator will be used by lesson create/update flows and by any student-facing lesson visibility checks. Readiness will not be stored in a new column because it is derived entirely from existing lesson content and source records.

Required lesson elements for approval:
- `title` and at least one of `objective` or `learning_objectives`
- non-empty `key_concepts`
- non-empty instructional sections for `hook`, `content`, `guided_practice`, `independent_practice`, and `assessment`
- at least one linked source with a non-empty `citation`
- any provided source `url` must be syntactically valid

The evaluator will not require activities for readiness. Activities are part of lesson delivery, but making them mandatory for approval would alter current content expectations and risks breaking existing progress flows.

Why this approach:
- It reuses the current lesson model.
- It avoids migrations for derived state.
- It keeps rules centralized instead of spreading ad hoc checks across routes.

Alternative considered:
- Add an `is_publish_ready` column and update it on every lesson write.
  - Rejected because it duplicates derived state and creates synchronization risk whenever nested sources change.

### 2. Review workflow will reuse `review_status` and `reviewed_by` with constrained transitions

The design keeps the current status values:
- `draft`
- `reviewed`
- `approved`

Transitions will become explicit:
- Any authorized lesson editor can create or edit a lesson in `draft`.
- Only a reviewer-capable user can move a lesson from `draft` to `reviewed`.
- Only a reviewer-capable user can move a lesson from `reviewed` to `approved`.
- Any reviewer-capable user can move `reviewed` or `approved` content back to `draft` when corrections are needed.

`reviewed_by` will be system-managed:
- It is set to the acting reviewer when a lesson is marked `reviewed` or `approved`.
- It is cleared when a lesson returns to `draft`.
- Clients will no longer be allowed to set an arbitrary reviewer id directly.

Why this approach:
- It builds directly on the existing fields instead of creating parallel review records.
- It improves integrity without forcing a larger workflow redesign.

Alternative considered:
- Keep `reviewed_by` writable by clients and only validate the status value.
  - Rejected because it allows users to impersonate reviewers and undermines governance.

### 3. Review-field permissions will be stricter than content-edit permissions

The current lesson routes allow `admin` and `teacher` users to create and update lessons. This design preserves that baseline for content fields, but review fields will be restricted to trusted reviewers using the systems already present in the backend:
- global `admin` users always have review privileges
- organization members with `content_admin` or `org_admin` have review privileges when an active org context is present
- standard `teacher` users can continue editing lesson content but cannot set `review_status` to `reviewed` or `approved`, and cannot set `reviewed_by`

This creates a separation between content authoring and content governance without changing the route layout.

Why this approach:
- It reuses the existing global-role and organization-role helpers in `app.deps`.
- It allows content creation to remain flexible while reserving governance actions for higher-trust roles.

Alternative considered:
- Allow teachers to mark lessons as `reviewed` and reserve only `approved` for admins.
  - Rejected because the goal is a credible governance layer, and a stronger separation between author and reviewer is the safer default.

### 4. Student-facing APIs will only expose approved and ready lessons

Lesson and course APIs will be split by audience using the existing routes:
- Authoring endpoints for admins and teachers continue to return all lessons, including `draft` and `reviewed`.
- Student-facing reads will only return lessons that are both `review_status == "approved"` and pass readiness evaluation.

For direct lesson access:
- student requests for non-approved or not-ready lessons will return not found or forbidden behavior consistent with the current route conventions

For course payloads:
- student-facing course responses will omit lessons that are not approved and ready
- teacher/admin course responses will continue to include all lessons

This keeps student lesson delivery aligned with governance status while preserving authoring visibility.

Why this approach:
- It does not introduce a second lesson storage model.
- It keeps existing course and lesson APIs intact while making audience-specific filtering explicit.
- It preserves progress behavior because students only progress through lessons that remain visible to them.

Alternative considered:
- Return all lessons to all roles and rely on the frontend to hide draft or unapproved content.
  - Rejected because policy enforcement must live on the backend, not only in the client.

### 5. Teacher notes will be role-gated; discussion questions will remain learner-visible

Frontend visibility will use the existing Angular lesson viewer and data flow:
- `teacher_notes` are treated as staff-only guidance and will be hidden for students
- `discussion_questions` remain visible to all lesson viewers because they function as part of instructional delivery rather than private annotation

Backend serialization should support this by nulling or omitting `teacher_notes` for student-facing responses. The frontend will also keep a defensive guard so teacher notes are not rendered when the viewer is in learner mode.

Why this approach:
- It matches the semantics of the fields already in the model.
- It minimizes frontend change.
- It avoids unnecessarily withholding legitimate student-facing prompts.

Alternative considered:
- Hide both `teacher_notes` and `discussion_questions` from students.
  - Rejected because discussion prompts are often intended for classroom participation and independent reflection.

### 6. Governance logic will live in shared helpers, not new service layers

Implementation should remain minimal by adding focused helpers close to the existing lesson routes and serializers:
- readiness evaluation helper
- review permission helper
- lesson visibility/serialization helper for student vs authoring responses

These helpers can be imported by both `lessons.py` and `courses.py` so governance rules are enforced consistently in direct lesson APIs and nested course payloads.

Why this approach:
- The current backend is route-centric.
- A small shared helper module is enough to avoid duplication without introducing unnecessary abstraction.

Alternative considered:
- Introduce a full lesson-governance service class hierarchy.
  - Rejected because the codebase does not currently use that pattern and the change does not justify it.

## Risks / Trade-offs

- [Existing draft content becomes hidden from students after enforcement] -> Filter only student-facing endpoints and keep teacher/admin authoring responses unchanged so content teams can still repair lessons.
- [Stricter approval rules may block previously acceptable lessons] -> Return actionable validation details listing missing readiness requirements instead of a generic error.
- [Role checks may be ambiguous when a request has no active org context] -> Use global `admin` as the unconditional reviewer role and require valid org reviewer membership when organization-scoped review privileges are needed.
- [Course payload filtering could change lesson counts for enrolled students] -> Limit filtering to unapproved or not-ready lessons and leave progress records untouched so existing completion data is not migrated or recomputed.
- [Frontend and backend gating could drift] -> Treat backend filtering as authoritative and use frontend gating only as a presentation safeguard.
- [Full lesson updates demote approved lessons by default] -> Mitigation: current `PUT /  lessons/{id}` behavior is intentionally full-update semantics, so omitted `review_status` defaults to `draft`. This is covered by tests, but future work should consider adding a PATCH endpoint or explicit edit workflow to avoid accidental approval demotion.

## Migration Plan

1. Add shared readiness, review-permission, and visibility helpers using the current lesson/source models.
2. Update lesson write paths so review fields are system-controlled and readiness is enforced on `reviewed`/`approved` transitions.
3. Update lesson and course read paths so student-facing responses filter out unapproved or not-ready lessons and suppress `teacher_notes`.
4. Apply minimal Angular updates so the lesson viewer hides teacher notes for learner views and handles missing unapproved lessons gracefully.
5. Add focused backend and frontend tests for workflow, readiness, and visibility behavior.

Rollback strategy:
- Revert the helper usage in routes and restore current unrestricted serialization behavior.
- No destructive data migration is required if readiness remains computed rather than stored.

## Open Questions

- Should `reviewed` lessons be visible to teachers outside authoring contexts, or should they behave the same as drafts until approved?
- When a student course becomes sparse because some lessons are filtered out, should the API expose a lesson count warning for instructors, or is silent omission sufficient for now?
- Should source URL validation accept any syntactically valid URL, or only `http`/`https` URLs?

## Enforcement Strategy

This change will use a phased enforcement approach.

Phase 1:
- Lessons must meet readiness rules to be marked as approved
- Student-facing APIs prefer approved lessons
- If no approved lessons exist, fallback behavior may return existing lessons

Phase 2 (future):
- Strict enforcement where only approved lessons are visible to students