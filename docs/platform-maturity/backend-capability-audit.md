# Backend Capability Audit

Date: 2026-07-23
Evidence baseline: `21c07367d664fcfdd128a7ca19e2f7e2f97b4b42`

## Method and classification

This audit checked route decorators and dependencies in `backend/app/api/routes/`, SQLAlchemy models in `backend/app/models.py`, request/response types in `backend/app/schemas.py`, Alembic history, pytest coverage, and Angular consumers. “Partial” means real persistence or behavior exists but does not support the complete named workflow. Active OpenSpec text alone is not implementation evidence.

## Content authoring

| Capability | Classification | Repository evidence and finding |
| --- | --- | --- |
| Course CRUD | Already supported for admin/teacher; authorization gap for content admin | `courses.py` exposes list/detail/create/update/delete plus `/courses/authoring`; `Course` and `CourseVersion` models persist ownership/version state; permission tests exist. Studio content admins cannot use the complete legacy CRUD safely. |
| Program CRUD | Partially supported | `programs.py` has list/detail/create/enroll; `Program` and `ProgramCourse.order` exist. No update, membership editing/reorder, archive, or delete route exists. |
| Curriculum hierarchy CRUD | Partially supported | `courses.py`, `units.py`, `lessons.py`, and `activities.py` provide real hierarchy mutations. Roles and ownership rules do not form a complete content-admin Studio workflow. |
| Unit CRUD | Already supported for existing author roles | `units.py` provides create/read/update/delete and version-scoped unit creation/listing; `Unit` has order and revision metadata. |
| Lesson CRUD | Already supported for existing author roles | `lessons.py` provides create/read/update/delete; `Lesson` owns activities, assessments, sources, reviewer, order, and review/revision fields. |
| Lesson ordering | Partially supported | `Unit.order`, `Lesson.order`, `Activity.order`, and `ProgramCourse.order` persist order, but there is no transactional reorder contract or concurrency handling. |
| Activity authoring | Partially supported | `activities.py` provides CRUD and `Activity` supports typed content/media/storybook pages. The schema is a generic string payload and lacks governed per-activity validation. |
| Assessment authoring | Partially supported | `assessments.py` provides list/detail/create and attempt submission. `Assessment` has lifecycle/revision fields, but no general update/delete/reorder route exists. |
| Question authoring | Partially supported | `QuestionCreateRequest` and `Question` persist prompts, choices, correct answer, explanation, points, and order as part of assessment creation; no independent edit/delete/reorder API exists. |
| Draft validation | Already supported for courses; partial elsewhere | `courses.py` exposes governance summary, publish readiness, safe-publish validation, competency integrity, lineage, and intervention evidence. Equivalent validation is not generalized to programs, assets, or all artifacts. |
| Preview behavior | Frontend-only gap over partial reads | Teacher preview reads course details without learner runtime. Studio artifact preview reads V2 artifacts. There is no general stateless author preview contract for unpublished curriculum. |

## Editorial workflow

| Capability | Classification | Repository evidence and finding |
| --- | --- | --- |
| Reviewer assignment | Data-model gap | `Lesson.reviewer_id` exists, but no scoped assignment workflow or API contract exists. V2 review records do not assign reviewers. |
| Review comments | Data-model gap | No review-comment model, route, or schema exists. Forum `Post` is not an acceptable substitute because it is unscoped and unauthenticated. |
| Requested changes | Partially supported | Product/artifact `review_state` and V2 review-status patch endpoints can record a state; no rationale, comment, or assignee is persisted. |
| Approval workflow | Partially supported | `/review-center`, artifact/product review-status patches, and `StudioReviewComponent` provide state transitions. Separation of duties and attributed decisions are absent. |
| Publishing lifecycle | Partially supported | Course-version publish and product publish routes exist; published timestamps and visibility state exist. No unified reversible lifecycle exists. |
| Archive and unpublish | Backend-only metadata / missing mutation | Course version enums include archived and product fields can represent nonpublic states, but no safe unpublish/rollback endpoint with dependency validation exists. |
| Version history | Partially supported | `CourseVersion`, revision/lineage fields on courses, units, lessons, and assessments, plus version create/update/publish routes are real. Broad list/history UX and immutable snapshots are incomplete. |
| Content diff | Backend-only gap | No diff service, schema, or endpoint exists. |
| Restoration | Backend-only gap | No restore mutation exists; lineage metadata is interpretive rather than a restoration workflow. |
| Audit history | Operational/data-model gap | Assessment attempt events exist for learning evidence, but no general authoring/review/admin audit-event model exists. |

## Assets and sources

| Capability | Classification | Repository evidence and finding |
| --- | --- | --- |
| Asset upload | Partially supported and hardened in Phase 7 | `uploads.py` stores coloring, storybook, and badge images for authorized roles. Phase 7 adds type/extension matching, a 5 MB limit, safe UUID names, and partial-file cleanup. There is no library contract. |
| Asset metadata | Partially supported | `Media` stores type/title/url/description; `KnowledgeSource` stores type, URI, citation, hash, status, metadata. Upload routes do not create governed metadata records. |
| Rights and attribution | Data-model gap | `Source.citation/url` and `KnowledgeSource.citation/metadata` are insufficient for license, rights holder, permission, and attribution policy. |
| Alt text | Data-model gap | `Media.description` is ambiguous; no required alt-text field or validation exists for image assets/storybook pages. |
| Asset reuse | Backend-only gap | Media can be referenced by activities, but there is no searchable scoped library or reuse API. |
| Asset replacement | Backend-only gap | No replacement/version mutation or dependent-reference safety exists. |
| Usage tracking | Backend-only gap | Relationships can reveal some direct references, but there is no usage endpoint or complete dependency graph. |
| Source management | Partially supported | Lesson `Source` rows and V2 `KnowledgeSource` list/create routes exist. Edit/delete, ownership, richer bibliography, and lifecycle are incomplete. |
| Source validation | Partially supported | `content_hash` and status fields exist, but URI reachability, rights, malware, provenance, and citation completeness are not validated. |

## Teacher capabilities

| Capability | Classification | Repository evidence and finding |
| --- | --- | --- |
| Persistent learner feedback | Data-model gap | Section, assignment, submission, assessment-attempt, and analytics reads exist; no teacher-feedback model or mutation exists. |
| Manual assessment review | Partially supported read / backend gap | Assessment attempts and answers persist; reporting endpoints summarize evidence. No teacher scoring/override/rubric review route exists. |
| Teacher comments | Data-model gap | No scoped teacher-comment model. Forum posts are not tied to a learner, assignment, or authorization boundary. |
| Retry workflow | Partially supported | `Assessment.max_attempts` and attempt history exist; no teacher-granted retry/exception workflow is implemented. |
| Discussion moderation | Critical authorization gap | `posts.py` and `threads.py` expose CRUD without authentication and accept caller-supplied `user_id`; no section/org scope or moderation state exists. |
| Learner intervention history | Partially supported | Analytics and runtime intervention recommendation/evidence endpoints exist, but no durable educator action/intervention-history model exists. |

## Organization capabilities

| Capability | Classification | Repository evidence and finding |
| --- | --- | --- |
| Branding | Partially supported profile | `Organization` has name, country, and timezone; org admin can patch the name. No logo/colors/contact rights model exists. |
| Bulk member import/export | Operational and backend gap | No job, file validation, preview, result, privacy-safe export, or rollback contract exists. |
| Organization audit events | Data-model gap | No organization audit-event model or route exists. |
| Organization announcements | Data-model gap | No audience-scoped announcement model or delivery contract exists. |
| Advanced organization reporting | Partially supported | Organization overview and section analytics provide scoped counts/aggregates; no metric definitions, privacy thresholds, or broad reporting/export API exists. |
| District/parent hierarchy | Future product decision | `Organization` has no parent relation. This is intentionally absent and must not be inferred from memberships. |
| Licensing/subscription | Future product decision | No license, entitlement, subscription, billing, or financial model exists. V2 pricing placeholders are not billing. |

## Platform capabilities

| Capability | Classification | Repository evidence and finding |
| --- | --- | --- |
| Moderation queues | Critical backend/authorization gap | V2 review center is editorial, not safety moderation. Forum content has no reports, flags, lock, restore, or authorized moderation queue. |
| User lifecycle states | Data-model gap | `User` has role and credentials but no active/disabled/deleted lifecycle, last-admin invariant, or restore semantics. |
| Badge lifecycle | Partially supported | Badge create/read/award exists; no edit, archive, delete, criteria version, or revocation workflow exists. |
| Platform audit logs | Operational/data-model gap | Phase 7 request logs add request IDs but no durable actor/action/resource audit events exist. |
| Notification infrastructure | Data-model and operational gap | No notification model, preference channel, queue, delivery adapter, retry, or receipt exists. |
| Search and indexing | Backend/operational gap | List endpoints use direct database queries; no cross-domain search contract or index exists. |
| Reporting | Partially supported | Analytics overview, teacher, learner, mastery, reporting, and section summaries exist; definitions, export, scheduling, privacy thresholds, and platform governance remain incomplete. |
| Data export | Backend/operational gap | No user/org/platform export contract, async job, retention, access logging, or secure download exists. |
| Data retention | Documentation and operational gap | Models contain timestamps but no retention schedule, deletion workflow, legal hold, or purge job exists. |

## Prior register corrections

- “No full curriculum CRUD” is reclassified to **substantial existing CRUD with a content-admin authorization/workflow gap**; course, unit, lesson, and activity mutations are real.
- “No version history” is reclassified to **partial version and lineage foundation**; course versions and revision metadata exist, but diff/restoration/history workflows do not.
- “No review workflow” is reclassified to **partial state workflow**; V2 review-center/status mutations exist, but attribution, comments, assignment, and audit history do not.
- “No asset support” is reclassified to **partial upload/media/source support without a governed library**.
- “No reporting” is rejected as too broad; multiple analytics endpoints exist. Advanced definitions, export, privacy, and operational delivery remain gaps.
- District hierarchy and licensing remain **future product decisions**, not defects in an existing workflow.
