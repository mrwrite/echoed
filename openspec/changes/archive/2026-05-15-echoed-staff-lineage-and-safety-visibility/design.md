## Context

EchoEd already has additive curriculum revision metadata, historical lineage coherence validation, learner-progress safety validation, assessment-evidence safety validation, publish-readiness visibility, safe-publish visibility, and governed learner delivery. The main gap is operational visibility: staff/admin users cannot yet inspect historical lineage and safety results through a bounded backend contract and staff-facing UI surface.

This change must stay inside the existing curriculum governance architecture. It should reuse the current `Course`/`Unit`/`Lesson`/`Assessment` model family, governance helpers, safe-publish validators, role-based access patterns, and premium UX state primitives. It must remain read-only, avoid workflow sprawl, and keep learner/student surfaces free of lineage warnings, rollback cues, and staff-only historical interpretation data.

## Goals / Non-Goals

**Goals:**
- Expose a staff-only, read-only lineage and safety endpoint that aggregates lineage coherence, learner-progress safety, assessment-evidence safety, and course-level safety interpretation.
- Present blocking issues and warnings in staff governance UI beside existing publish-readiness and safe-publish sections.
- Preserve learner-safe separation so learner-facing routes and governed delivery do not expose staff-only lineage warnings or controls.
- Add focused regression coverage for access boundaries, read-only behavior, UI rendering, and compatibility with current reporting, certification, and governed delivery behavior.

**Non-Goals:**
- Implement publish, republish, rollback, archival, or migration workflows.
- Introduce mutation endpoints or write-side lineage controls.
- Replace existing safe-publish validation or reporting contracts with a new governance engine.
- Redesign curriculum routes, create a new CMS surface, or add learner-facing lineage features.
- Change grading, mastery, certification, or governed progression semantics.

## Decisions

### Decision: Add a dedicated staff-only lineage/safety read model rather than overloading learner-safe contracts

The cleanest boundary is a staff-only course-scoped contract that aggregates existing validation helpers into one read-only payload. This avoids polluting learner-safe serialization with staff-only warnings and keeps the UI integration explicit.

Alternatives considered:
- Add lineage warnings directly into learner-safe course serialization: rejected because it violates learner-safe separation.
- Fold all lineage results into the existing safe-publish payload only: rejected because it over-couples distinct governance concerns and makes dedicated staff UI rendering less explicit.

### Decision: Reuse existing validation helpers and aggregate results rather than creating new safety engines

The backend contract should compose lineage coherence, learner-progress safety, assessment-evidence safety, and course-level safe-publish interpretation from current helpers. This preserves prior behavior and reduces the risk of drift between staff visibility and the underlying governance logic.

Alternatives considered:
- Recompute safety rules in a new endpoint-specific layer: rejected because duplicate rules will drift from canonical validators.
- Persist lineage/safety snapshots: rejected because the requirement is bounded, read-only visibility, not a workflow or snapshot system.

### Decision: Integrate staff visibility into existing governance surfaces beside publish-readiness and safe-publish sections

Staff already inspect governance status through bounded course-management surfaces. Lineage and safety context should appear adjacent to publish-readiness and safe-publish sections so staff can interpret historical risks without navigating a separate dashboard.

Alternatives considered:
- Dedicated lineage console or dashboard: rejected because it adds product surface area before the operational need exceeds the current governance experience.
- Hide lineage warnings behind reporting-only views: rejected because governance review needs direct access before or alongside reporting consumption.

### Decision: Keep role access aligned to existing staff/admin/content patterns

The new backend contract and UI should be available only to authorized staff/admin/content roles, using the same existing auth/session authority patterns as other governance surfaces. Student and learner-facing requests must continue to receive no staff-only lineage data.

Alternatives considered:
- Introduce a new lineage-specific permission model: rejected because it adds auth complexity without evidence that existing governance roles are insufficient.
- Expose to all authenticated users: rejected because lineage and safety interpretation is explicitly staff/admin scoped.

### Decision: Treat UI integration as read-only status presentation with canonical state handling

The UI should render aggregate safety status, blocking issues, warnings, and affected entities using the same loading, empty, error, and bounded-panel patterns already used for governance and premium UX primitives. It must not add publish, rollback, or mutation controls.

Alternatives considered:
- Add inline fix actions or rollback buttons: rejected because this change is not a workflow initiative.
- Hide issues unless a course is actively being published: rejected because staff may need historical inspection outside a publish action.

## Risks / Trade-offs

- [The aggregated staff endpoint may duplicate information already available in safe-publish validation] -> Mitigation: define the new contract as an explicit lineage/safety view that reuses existing validators and presents their results in a staff-consumable shape.
- [UI surfaces could become cluttered with warnings] -> Mitigation: group issues into blocking issues and warnings, include affected entity labels, and keep the surface adjacent to current governance panels rather than expanding into a separate workflow.
- [Role-boundary regressions could leak staff-only warnings to learners] -> Mitigation: add focused tests for learner denial and learner UI non-exposure.
- [Endpoint behavior could accidentally mutate safety-related records through reused services] -> Mitigation: keep the implementation read-only and add regression coverage proving no mutation across curriculum, progress, attempts, events, certifications, mastery, or reporting state.
- [Staff may misinterpret historical warnings as workflow affordances] -> Mitigation: explicitly exclude publish/rollback buttons and position the surface as read-only governance context.

## Migration Plan

1. Add a bounded staff-only backend contract that aggregates lineage and safety results from existing validation helpers.
2. Integrate staff-facing lineage and safety panels into current governance/course-management UI beside publish-readiness and safe-publish sections.
3. Extend regression coverage for authorization, read-only behavior, staff rendering, learner non-exposure, and compatibility with current reporting and governed delivery behavior.
4. Defer any future workflow actions, mutation endpoints, or expanded lineage tooling to later changes.

Rollback strategy:
- Remove or hide the staff-only endpoint and UI surface if needed, while preserving the underlying lineage metadata and safety validation helpers.
- Because the change is additive and read-only, rollback does not require rewriting curriculum, learner progress, assessment evidence, mastery, or certification records.

## Open Questions

- Whether the staff endpoint should remain dedicated to course scope first or later expand to unit/lesson/assessment scope as separate read-only views.
- Whether lineage/safety results should be loaded on demand in the staff UI or bundled with existing governance fetches.
- How much issue de-duplication should occur between lineage/safety panels and current safe-publish views when the same underlying blocker appears in both contexts.
