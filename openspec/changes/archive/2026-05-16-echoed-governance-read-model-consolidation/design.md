## Context

EchoEd already has the underlying governance signals this initiative needs: publish-readiness rules, safe-publish validation, historical lineage and learner-safety validation, staff lineage visibility, competency-evidence integrity, runtime intervention intelligence, governed learner delivery, and bounded premium staff UX primitives. The current gap is not missing governance logic. The gap is that staff-facing dashboards still need multiple per-course reads and route-local orchestration to assemble those signals into something operationally useful.

This change therefore needs to stay thin and additive. The existing validators and read helpers remain authoritative. The new architecture should only compose them into one deterministic, read-only course governance summary contract for staff/admin/teacher consumption. It must not become a publish workflow, rollback workflow, grading workflow, intervention workflow, or learner-facing payload expansion.

Key constraints:
- Preserve current learner-facing delivery and serialization contracts.
- Reuse existing staff/admin/content authorization boundaries and deny learners/students.
- Avoid route-level duplication by introducing one shared backend composition boundary.
- Keep all evaluation deterministic and read-only, with no mutation to curriculum, progression, assessment, certification, or reporting state.
- Define scale boundaries for batching and pagination, but defer complex caching implementation.

## Goals / Non-Goals

**Goals:**
- Define one course-scoped governance summary payload that aggregates publish readiness, safe-publish validation, lineage safety visibility, competency-evidence integrity, and runtime intervention guidance.
- Centralize composition in a shared backend read-model layer so existing validators are reused and route-local orchestration is reduced.
- Allow existing staff/admin/teacher surfaces to fetch one governance payload per course while preserving current section structure and bounded UX semantics.
- Keep authorization and learner-safety boundaries explicit: staff/admin/content allowed, learners denied, learner contracts unchanged.
- Define performance expectations for batch access, pagination, and future cacheability without requiring a new cache subsystem.
- Add focused verification requirements for payload shape, access control, read-only behavior, non-mutation, frontend request reduction, and preservation of existing validator correctness.

**Non-Goals:**
- Introducing a new publish, republish, rollback, archival, grading, certification, reporting, or intervention workflow.
- Replacing existing validators with a new governance engine or persisting a second source of truth.
- Expanding learner-facing payloads with staff governance metadata.
- Adding mutation endpoints, automatic fixes, override controls, or dashboard action expansion.
- Implementing complex precomputed caches, background refresh jobs, or materialized read stores in this change.

## Decisions

### Decision: Define one canonical course governance summary payload over existing validators

The primary contract should be a single course-scoped staff payload that contains bounded sections for publish readiness, safe-publish validation, lineage safety, competency integrity, and runtime intervention recommendations. Each section should carry its own aggregate status and structured issues while preserving the semantics of the underlying validator that produced it.

Why this over continuing to fetch each source independently:
- It reduces frontend request fan-out and repeated per-route orchestration.
- It makes staff governance review deterministic and easier to test.
- It preserves current section boundaries while still giving staff one payload to consume.

Alternatives considered:
- Continue with multiple route-level requests and aggregate only in the frontend. Rejected because it preserves duplication, inconsistent composition, and unnecessary request growth.
- Flatten all governance concerns into one unstructured issue list. Rejected because staff still need publish, lineage, competency, and runtime sections to remain distinguishable.

### Decision: Introduce a shared backend read-model composition layer rather than a new router family per concern

The backend should expose one shared composition boundary that calls the existing deterministic validators and read helpers, normalizes their outputs into the course governance summary shape, and can be reused by current or future staff routes. This keeps orchestration out of route handlers and avoids coupling every UI surface to five separate domain helpers.

Why this over direct route-level orchestration:
- It creates one canonical composition path.
- It reduces drift between staff surfaces.
- It keeps the read model reusable without redefining domain authority.

Alternatives considered:
- Put the aggregation logic directly inside one dashboard route. Rejected because the duplication would return when other staff surfaces need the same summary.
- Persist summary snapshots. Rejected because the current need is bounded read-only composition, not a separate storage system.

### Decision: Keep underlying validators authoritative and read-only

The summary layer must not recompute publish readiness, safe publish, lineage safety, competency integrity, or runtime intervention logic from scratch. It should invoke the existing validators and only compose their results. Any section-level status or issue counts in the summary should be derived from returned results rather than inferred through new side logic.

Why this over reimplementation:
- Reuse preserves prior governance behavior.
- Duplicate rules would drift quickly across safety-sensitive domains.
- Read-only composition is much safer than inventing a new cross-domain governance engine.

Alternatives considered:
- Create summary-specific mini-validators per section. Rejected because it duplicates normative logic.
- Loosen determinism with heuristic cross-section rollups. Rejected because governance needs auditable, source-backed summaries.

### Decision: Preserve staff UX sections while switching to one payload per course

The frontend should continue to render the existing bounded governance sections initially, but those sections should read from one course governance payload instead of issuing separate per-course requests. The UX remains additive: one payload, same staff-readable sections, no new action surfaces.

Why this over redesigning the governance UI:
- It minimizes product change and regression risk.
- It achieves the operational benefit without inventing a new dashboard experience.
- It keeps the initiative aligned with the stated non-goals.

Alternatives considered:
- Introduce a brand-new consolidated governance console. Rejected because it expands product scope.
- Hide individual sections behind a generic summary card. Rejected because staff still need section-specific interpretation.

### Decision: Enforce current authorization boundaries and explicit learner denial

The contract should reuse existing staff/admin/content access checks and explicitly deny learner/student access. Learner-facing routes, governed delivery contracts, and progress payloads should not be expanded with governance summary fields, even if they reference the same course.

Why this over broader access:
- These signals are operational and staff-scoped.
- Prior governance work already established learner-safe separation.
- Wider access would create product and privacy risk without a learner requirement.

Alternatives considered:
- Expose limited summary metadata to all authenticated users. Rejected because it weakens staff-only governance boundaries.
- Piggyback the summary into learner course contracts. Rejected because it changes learner payload semantics and risks leakage.

### Decision: Define scale boundaries around batch reads and future caching, but defer cache implementation

The design should require the composition layer to support bounded batching and pagination expectations so staff dashboards do not degenerate into N+1 growth when viewing multiple courses. At the same time, this change should avoid building complex caches before the canonical summary shape is stabilized.

Why this over immediate caching:
- The bigger current problem is contract and composition fragmentation, not cache absence.
- Stabilizing the summary shape first lowers future cache invalidation risk.
- Batching and shared composition deliver meaningful improvement without extra infrastructure.

Alternatives considered:
- Build a precomputed governance summary cache immediately. Rejected because it adds invalidation and freshness complexity too early.
- Ignore batch considerations until later. Rejected because request fan-out is a named objective of this change.

## Risks / Trade-offs

- [Summary composition could mask differences between source validators] -> Mitigation: preserve section-specific statuses, issue lists, and bounded section identity instead of flattening all results.
- [A shared composition layer can become a de facto second governance engine] -> Mitigation: keep it strictly compositional, reuse existing validators, and prohibit new write-side behavior.
- [Frontend consolidation may still leave hidden fan-out inside the backend] -> Mitigation: define batching and pagination expectations in the service boundary and verification requirements.
- [Staff-only payloads could leak into learner flows through shared schema reuse] -> Mitigation: keep explicit staff-only contracts and add learner-denial and learner-non-exposure regression coverage.
- [Future caching may be harder if the initial payload shape is too broad] -> Mitigation: keep the summary course-scoped and section-bounded, and defer cache implementation until the shape proves stable.

## Migration Plan

1. Define the canonical course governance summary contract and the shared read-model composition boundary in spec form.
2. Update relevant existing governance specs so publish readiness, safe-publish validation, lineage safety, competency integrity, runtime recommendations, and bounded staff UX can participate in the summary.
3. Implement the shared backend composition path and expose it through existing or minimally extended staff-facing contracts.
4. Update staff/admin dashboard consumers to request one governance payload per course while preserving the current section layout.
5. Add focused regression coverage for authorization, read-only safety, non-mutation, payload shape, request reduction, and validator preservation.
6. Defer advanced caching and any workflow actions to future changes once real usage patterns are clear.

Rollback strategy:
- Remove or disable the additive composition layer and staff consumption path while leaving the underlying validators intact.
- Because the change is read-only, rollback does not require curriculum, progression, evidence, certification, or reporting data repair.

## Open Questions

- Whether the first implementation should expose only course-scoped summaries or also include an optional lightweight nested preview for unit or lesson issue counts.
- Whether existing staff surfaces should fetch the summary eagerly with course governance data or lazily when governance sections expand.
- How much issue de-duplication is desirable when the same blocker appears in both publish-readiness and safe-publish sections.
