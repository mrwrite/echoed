## Context

EchoEd already has the core ingredients for governed institutional curriculum delivery: Course, Unit, Lesson, Activity, and Source models; lesson readiness and review logic; assessment/mastery foundations; flagship pathway content; and premium UX state primitives. What is still missing is a bounded governance layer that allows staff to safely create, revise, review, approve, publish, and maintain curriculum across many pathways without introducing a second curriculum system, corrupting learner progression, or turning the platform into a full LMS authoring suite.

The next stage must support pathway growth across flagship cultural learning, core academics, STEM, GED/adult education, and enrichment while preserving one canonical content and delivery model. That means authoring and publishing governance has to remain additive, role-aware, and compatible with historical learner progress and evidence records.

## Goals / Non-Goals

**Goals:**
- Define a canonical curriculum lifecycle for draft, review, approved, and published content.
- Reuse and extend existing lesson governance authority where it already fits the problem.
- Add bounded publish-readiness, preview, versioning, and maintenance rules that preserve learner-safe delivery.
- Define scalable governance expectations for aligned assessments and mastery compatibility.
- Keep authoring UX bounded to educator and content-admin surfaces with clear readiness and compliance signals.
- Preserve historical learner progress, attempts, mastery evidence, and certification integrity when content evolves.

**Non-Goals:**
- Building a full LMS authoring suite, marketplace, or public creator platform.
- Rewriting the Course, Unit, Lesson, Activity, or Source model.
- Creating a separate curriculum database or a parallel pathway/progression engine.
- Introducing AI-generated curriculum workflows.
- Expanding into grading, messaging, or broad operational workflow automation beyond bounded governance.

## Decisions

### 1. Keep the existing curriculum model as the canonical content backbone
The implementation SHALL preserve Course, Unit, Lesson, Activity, Source, and existing lesson governance as the canonical curriculum foundation rather than introducing a separate pathway or authoring model.

Rationale:
- This keeps learner delivery, serialization, and progress resolution on one content backbone.
- It avoids divergence between authored content and delivered content.

Alternative considered:
- Introduce a parallel authoring-only content graph. Rejected because it increases migration complexity and risks curriculum drift.

### 2. Treat publishability as governed state, not simple staff visibility
Publishing SHALL be governed by explicit readiness validation, ordering checks, source expectations, learner-safe visibility rules, and role-aware preview behavior rather than by ad hoc staff access alone.

Rationale:
- Learner delivery integrity depends on content being structurally and academically ready before publication.
- This preserves unavailable-state semantics before learner release.

Alternative considered:
- Allow staff to publish any draft content manually. Rejected because it weakens institutional quality and learner-safe boundaries.

### 3. Version curriculum additively and preserve historical learner safety
Published curriculum changes SHALL use additive version metadata and bounded revision semantics so active learner progress, historical attempts, mastery evidence, and certifications remain trustworthy.

Rationale:
- Published content evolves over time, but learner history must remain interpretable.
- Historical safety is more important than unrestricted edit flexibility.

Alternative considered:
- Allow in-place edits to published content with no governance distinction. Rejected because it risks historical evidence ambiguity and progression corruption.

### 4. Keep authoring UX bounded to readiness, review, and publishing support
Educator and content-admin authoring UX SHALL focus on readiness indicators, review queues, missing-field guidance, source/compliance warnings, and publish-state clarity instead of expanding into a full workflow or LMS-style operation center.

Rationale:
- The system needs institutional governance, not authoring-suite sprawl.
- Existing premium UX primitives can carry much of the necessary state treatment.

Alternative considered:
- Build a broad curriculum operations console with workflow orchestration. Rejected because it exceeds the bounded scope and would be hard to scale responsibly.

### 5. Reuse the existing assessment/mastery foundation for governance checks
Assessment readiness, competency alignment, learner availability gating, and historical evidence preservation SHALL build on the current assessment/mastery architecture rather than inventing a separate academic governance subsystem.

Rationale:
- The platform already has a canonical assessment and mastery layer.
- Governance checks should strengthen that system, not duplicate it.

Alternative considered:
- Build an independent assessment approval and evidence store for authoring. Rejected because it fragments academic integrity.

## Risks / Trade-offs

- [Governance rules become too strict for authors] -> Keep validations explicit, explainable, and staged so authors can see what is missing before review or publish.
- [Published revision rules become too weak] -> Distinguish draft revisions and material changes clearly, and preserve historical learner safety as the stronger constraint.
- [Authoring UX grows into LMS complexity] -> Bound the UX to readiness, review, preview, and publish workflows, and reuse existing educator/admin architecture.
- [Pathway-specific needs pressure the model into fragmentation] -> Keep one canonical curriculum governance system with additive metadata for pathway-specific nuance.
- [Assessment governance drifts from delivery governance] -> Reuse existing assessment availability and mastery-alignment foundations as the governing source of truth.

## Migration Plan

1. Extend existing governance contracts and rules additively around course, unit, lesson, and assessment readiness.
2. Add publish-readiness and preview behavior without changing learner route structure or progression resolution.
3. Introduce bounded version/revision semantics for published curriculum and protect historical learner state.
4. Add focused educator/content-admin UX only where governance state must be inspected or acted on.
5. Verify that learner-safe serialization, governed delivery, assessment evidence, and certification behavior remain compatible throughout rollout.

## Open Questions

- Which parts of publish readiness belong in `lesson_governance.py` versus adjacent governance helpers for course and pathway scope?
- How should material versus minor published edits be classified without overcomplicating the authoring workflow?
- Which existing educator/admin surface should host the first bounded review queue or publish-readiness view?
- How much assessment alignment should be required before course-level publication versus lesson-level publication?
