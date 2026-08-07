# Course Authoring Domain Inventory

This inventory maps the existing EchoEd domain to the unified course-authoring aggregate. It is an implementation aid, not a second curriculum contract.

## Canonical aggregate

| Authoring concern | Canonical model and fields | Existing creation-path behavior | Unified behavior |
| --- | --- | --- | --- |
| Course identity | `Course.id`, `title`, `description`, `subject`, `age_band_min`, `age_band_max`, `default_locale` | Legacy wizard only sends title and description; `/courses/authoring` accepts the complete identity but creates no graph. | One aggregate accepts and returns every supported identity field. |
| Alignment metadata | `Course.learning_objectives`, `skill_tags`, `standards_metadata` | Accepted by APIs but mostly absent from UI. | Setup and quality views use the same canonical fields. |
| Ownership and scope | `Course.created_by`, `organization_id` | Legacy writes can create unscoped courses; organization authoring scopes only the shell. | Capability resolver and aggregate service enforce organization scope and creator relationship. |
| Draft revision and recovery | `Course.revision_number`, `revision_status`, `revision_metadata`, `updated_at`; `CourseVersion` | Client-side wizard state is posted at the end; course versions are disconnected from graph editing. | `revision_number` is the optimistic concurrency token; `revision_status` and `CourseVersion.status` represent lifecycle; idempotency and template origin are stored in `revision_metadata`. |
| Units | `Unit` and `Course.units` | Legacy create/update persists units and recreates the entire graph during update. | Transactional aggregate normalizes deterministic order and preserves supplied identifiers when they belong to the draft. |
| Lessons | `Lesson` and `Unit.lessons` | Legacy path persists rich lesson content and review fields. | Aggregate reuses all instructional and educator-only fields while centralizing review-field authorization. |
| Activities and storybooks | `Activity`, `StorybookPage` | Created in the wizard review step. | Edited in the persistent outline; media continues to use the canonical upload/media services. |
| Sources | `Source` | Persisted by legacy nested writes. | Persisted by the aggregate and preserved during duplication. |
| Assessments | `Assessment`, `Question`, `AssessmentCompetencyAlignment` | Separate assessment APIs and relationships. | Aggregate returns assessment references; assessment content remains owned by the existing assessment engine. |
| Review | `Lesson.review_status`, `reviewed_by`; V2 review wrappers and governance services | Review checks are disconnected from course creation. | Studio lifecycle actions call the existing review/governance boundaries; no parallel review table is introduced in the first slice. |
| Versions and publication | `CourseVersion`, `Course.published_at`, nested `published_at`, safe-publish/readiness services | Organization endpoint creates a draft version; a separate endpoint publishes it. | Every durable draft has a current version, and learner visibility changes only through governed publication. |

## Creation-path convergence

- `POST /api/courses` and `PUT /api/courses/{id}` are retained temporarily for compatibility and delegated to the canonical aggregate service.
- `POST /api/courses/authoring` becomes the idempotent organization-aware creation boundary.
- The shallow `StudioCoursesComponent` form and `CourseWizardComponent` are migration sources only; the canonical Angular Studio uses one authoring service and one durable draft route.
- Learner-facing course and lesson serializers remain authoritative for delivery and preview filtering.

## Metadata reuse decisions

- No new draft table is required for the first slice.
- `Course.revision_number` is the concurrency token.
- `Course.revision_status` carries `draft`, `submitted`, `approved`, `published`, or `changes_requested` during authoring.
- `Course.revision_metadata` stores bounded authoring metadata such as idempotency key, template origin, derivative source, last submission, and review feedback.
- `Course.updated_at` is the visible durable-save timestamp.
- A data migration is required only to normalize older editable course records to a non-null revision number/status/metadata; existing schema columns already support the contract.
