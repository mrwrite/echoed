## Context

EchoEd has one canonical course, unit, lesson, and activity hierarchy, but authoring is exposed through two incomplete paths. `StudioCoursesComponent` lets content and organization administrators create empty records through the legacy course endpoint, while `CourseWizardComponent` edits the nested graph through routes and APIs limited to platform-level `admin` and `teacher` roles. A separate organization-scoped authoring endpoint and course-version model already exist, but they are not connected to the nested editor. Governance summaries, staff preview, review state, and safe-publish checks also exist outside the creation journey.

The stakeholders are content administrators who build canonical curriculum, organization administrators who manage scoped offerings, teachers or instructors who may adapt content within policy, reviewers and publishers who approve release, platform administrators who oversee the system, and learners whose delivery view must never expose drafts. The implementation must extend existing routes, models, schemas, role guards, organization membership rules, version records, and governance services rather than create parallel curriculum or approval engines.

## Goals / Non-Goals

**Goals:**

- Provide one discoverable, responsive course studio from creation through governed release.
- Make backend capability and organization scope authoritative while keeping frontend navigation consistent with those decisions.
- Persist the complete canonical course graph safely through autosave and explicit save, with visible state, conflict detection, and idempotent creation.
- Support fast outline construction, inline editing, duplication, deterministic ordering, quality guidance, staff preview, review submission, and safe publication.
- Reuse canonical metadata, source attribution, assessment, governance, and version structures.
- Meet WCAG 2.2 AA interaction expectations, including keyboard operation and non-drag reorder alternatives.
- Introduce bounded template, duplication, and import/export extension points without blocking the core authoring release.

**Non-Goals:**

- No new curriculum hierarchy, learner runtime, review engine, permission store, assessment engine, or media store.
- No simultaneous multi-user editing or real-time cursor collaboration in the initial release.
- No AI-generated course execution in this change.
- No claim of Common Cartridge, QTI, LTI, SCORM, Quality Matters, or OSCQR certification.
- No automatic publication merely because a course passes automated checks.

## Decisions

### Initial authorization policy

The first implementation uses the following explicit policy. Backend-derived capabilities remain authoritative, and a future organization policy layer may narrow these defaults without changing the editor contract.

| Actor | Initial course-authoring policy |
| --- | --- |
| `content_admin` organization member | Create organization drafts; edit organization drafts; duplicate permitted courses; preview; submit for review. Cannot approve or publish. |
| `org_admin` or organization `super_admin` member | All content-admin actions plus review decisions and governed publication within that organization. |
| `teacher` or `instructor` organization member | Duplicate an approved or published permitted course into an organization-scoped derivative; edit drafts they created; preview; submit for review. Cannot edit canonical published content in place, approve, or publish. |
| Platform `admin` or `super_admin` | Platform oversight plus explicit create, edit, duplicate, preview, review, and publish authority for migration compatibility and incident response. |
| Learner, parent, viewer, inactive or invited member | No authoring, review, or publication actions. |

Review independence is enforced by preventing content administrators and teachers from approving their own submissions. Organization administrators are the initial reviewer role because the current organization-role enum has no separate reviewer role. Adding a dedicated reviewer role remains a later policy enhancement.

1. **Use one organization-aware aggregate authoring contract over the canonical course graph.**
   - The authoring API will create, read, and update course metadata together with ordered units, lessons, activities, sources, and assessment references using existing domain models and route modules.
   - Existing learner reads remain audience-filtered and unchanged. Legacy course create/update routes remain temporarily as compatibility adapters and are removed from frontend authoring navigation after migration.
   - Alternative: keep shell creation and nested editing as separate workflows. Rejected because it preserves permission drift, duplicate records, and unclear ownership.

2. **Represent authorization as backend-derived capabilities within organization scope.**
   - Responses needed by Studio will expose bounded actions such as `can_create`, `can_edit`, `can_submit_review`, `can_review`, and `can_publish`; the backend remains authoritative for every mutation.
   - Default policy: content administrators author and submit; organization administrators author, assign, and publish where organization policy permits; teachers or instructors adapt assigned or permitted content; reviewers decide review outcomes; platform administrators oversee and may act only where explicitly authorized.
   - Alternative: reproduce role-name arrays in each Angular route. Rejected because the current drift demonstrates that route-only role lists are not reliable authorization.

3. **Use a server-authoritative draft with optimistic concurrency and idempotent creation.**
   - Initial creation returns a durable draft ID. Subsequent debounced autosaves and explicit saves send a revision token; stale updates return a conflict outcome rather than silently overwriting newer work.
   - Creation uses an idempotency key so retries cannot create duplicate drafts. The editor displays saving, saved, offline or failed, and conflicted states and keeps unsaved input available for retry.
   - Alternative: retain a singleton client-side `BehaviorSubject` until final POST. Rejected because refresh, navigation, multiple tabs, and network failures can lose or duplicate work.

4. **Use a persistent outline editor with focused detail panels.**
   - Course structure remains visible while creators add or edit units, lessons, and activities. Setup, build, quality, preview, and release are modes over the same durable draft rather than disposable wizard pages.
   - Reordering supports drag and drop plus Move up, Move down, and position controls. Destructive actions require contextual confirmation and preserve deterministic ordering.
   - Alternative: extend the existing four-step wizard. Rejected because activity creation is currently hidden in review, previous context disappears, and creators cannot efficiently revise the overall structure.

5. **Separate authoring validation from governed release decisions.**
   - Drafts may remain incomplete. Inline validation explains field-level problems, while a quality panel aggregates completeness, measurable objectives, objective/activity/assessment alignment, source and media issues, accessibility prompts, and canonical governance readiness.
   - Submission and publication use existing review and safe-publish semantics. Automated checks inform authorized humans and never bypass review authority.

6. **Make staff preview use learner serialization without learner availability.**
   - Preview renders the learner-safe projection of the selected durable draft or version for authorized staff, excluding educator-only fields exactly as learner delivery does, but without making the content learner-visible.
   - Alternative: preview the authoring object directly. Rejected because it would not expose audience-filtering defects before release.

7. **Treat templates and exchange formats as adapters at the boundary.**
   - Blank creation, internal templates, and course duplication normalize into the same authoring aggregate. Import/export adapters also map to this aggregate and return a validation report before persistence.
   - The first slice may deliver blank, duplicate, and internal-template creation while defining interfaces and tests for later Common Cartridge and QTI adapters.

8. **Retire authoring controls from oversight-only pages.**
   - Admin course oversight continues to expose governance and high-impact administrative actions. All create/edit links route to the canonical Studio only when the capability payload permits them.
   - The shallow Studio draft form and legacy wizard routes are removed after migration and deep links redirect to the corresponding Studio draft.

## Risks / Trade-offs

- **Nested aggregate saves could become large or slow** → Use bounded payloads, transactional persistence, normalized client state, and later incremental entity endpoints only where profiling demonstrates need.
- **Autosave could create write contention or stale overwrites** → Debounce changes, serialize writes per draft, use revision tokens, and provide an explicit conflict-resolution path.
- **Role policy may differ between organizations** → Centralize capability calculation and keep organization publishing policy configurable rather than hard-code frontend role assumptions.
- **Legacy and new routes may diverge during migration** → Make legacy writes call the same domain service, add contract tests, instrument remaining legacy usage, and time-box compatibility.
- **Quality guidance could overwhelm occasional authors** → Use progressive disclosure, plain-language explanations, direct links to the affected item, and separate blocking issues from recommendations.
- **Import complexity could expand scope** → Ship boundary interfaces and validation reports first; treat certified format coverage as separate follow-on work.
- **Course graph deletion can disrupt active learners** → Prefer archive and version replacement in the Studio; preserve existing permanent deletion only in explicit administrative oversight until a recoverable archive contract is complete.

## Migration Plan

1. Add capability calculation, draft ownership or revision metadata where absent, idempotent creation, and transactional aggregate save services behind existing course route modules.
2. Add role-matrix and course-graph contract tests before changing navigation.
3. Build the canonical Studio editor and point content-admin and organization-admin entry points to it behind a feature flag.
4. Connect quality, preview, review submission, versioning, and safe publish; verify learner isolation throughout.
5. Migrate legacy editor deep links to Studio, retain compatibility adapters for one release window, and measure remaining use.
6. Remove the shallow Studio form and legacy wizard navigation after data and journey verification; preserve rollback by re-enabling the feature flag and adapters.
7. Add template and duplication flows, then deliver import/export adapters as bounded follow-on slices.

## Open Questions

- What conflict-resolution UX is acceptable for simultaneous edits from two browser tabs before real-time collaboration exists?
- Which initial templates are product-owned, and who can create organization-specific templates?
- Is Common Cartridge import/export required for the first production release or only the adapter contract and internal template format?
