## Context

EchoEd already has governed learning delivery, lesson-source governance, canonical auth/org/session authority, and progression state. The missing layer is a trustworthy institutional assessment system that can support mastery-based learning, educator grading, evidence retention, and future reporting without becoming a separate grading or progression engine.

This change must operate on top of the existing course/unit/lesson/activity hierarchy and the existing progress and lesson-session systems. The goal is not a lightweight quiz feature. The goal is a durable institutional assessment foundation that can support homeschool credibility, school-style grading, intervention workflows, and future transcript/reporting needs.

## Goals / Non-Goals

**Goals:**
- Create one canonical assessment model that covers lesson, unit, course, formative, summative, and mastery-check use cases.
- Keep assessment evidence, grading, and mastery grounded in governed academic records rather than route-local or UI-local state.
- Reuse the existing auth/org/session authority and governed progression stack.
- Support educator assignment, review, manual grading, rubric-based evaluation, and cohort insight.
- Support learner-facing assessment delivery, attempt lifecycle, explicit unavailable states, and mastery feedback.
- Define the institutional reporting shape needed for gradebook and transcript readiness.

**Non-Goals:**
- Building a full SIS or transcript export product in this phase.
- Replacing the existing lesson governance or progress systems.
- Introducing a parallel assessment engine, a separate mastery database, or a disconnected grading workflow.
- Redesigning the UI beyond what the assessment foundation requires.

## Decisions

1. **Assessment is a governed domain layered on the existing academic hierarchy.**
   Assessments will attach to lessons, units, and courses instead of inventing a separate course tree. This keeps assessment aligned with already-governed delivery and progression.
   - Alternative considered: a standalone assessment service with its own content graph.
   - Rejected because it would duplicate hierarchy, governance, and eligibility logic and would drift from lesson/session authority over time.

2. **Assessment type and lifecycle are canonical and shared across all callers.**
   Formative, summative, lesson-level, unit-level, course-level, and mastery-check assessments should all use the same state model and attempt flow, with visibility controlled by role and context.
   - Alternative considered: endpoint-specific states and bespoke flows for learner, educator, and reporting surfaces.
   - Rejected because it would create inconsistent grading legitimacy and make auditability weaker.

3. **Attempt history is immutable evidence, and grading is append-only.**
   A submission becomes a durable evidence record with review and grading events layered onto it. Corrections, overrides, and educator reviews should preserve the original attempt trail.
   - Alternative considered: mutating a single submission row in place.
   - Rejected because institutions need auditability, provenance, and trustworthy intervention history.

4. **Mastery is derived from evidence and thresholds, not from ad hoc completion flags.**
   Mastery should aggregate from lesson evidence upward to unit and course readiness, with clear thresholds and intervention triggers.
   - Alternative considered: one boolean mastery marker per learner and course.
   - Rejected because it cannot express rubric-based competency, partial mastery, or remediation needs.

5. **Educator and learner experiences consume the same authoritative assessment records.**
   Educator assignment, grading, rubric review, and intervention insight will read from the same records the learner sees, filtered by permissions and release policy.
   - Alternative considered: separate educator-facing assessment objects and learner-facing results.
   - Rejected because it risks divergence between what was assigned, what was graded, and what was reported.

6. **Assessment influences progression through existing progress authority rather than replacing it.**
   Assessment outcomes should inform mastery and progression eligibility in the current governed progression pipeline, not create a second progression engine.
   - Alternative considered: a parallel “assessment progression” service that directly advances learners.
   - Rejected because it would fragment authority and weaken current lesson-session integrity.

## Risks / Trade-offs

- [Complex state model] → Mitigate by keeping a single canonical assessment lifecycle and explicit status transitions.
- [Migration and backfill work] → Mitigate by introducing assessment records additively and mapping existing progress concepts where possible.
- [Performance of reporting and mastery aggregation] → Mitigate by deriving summaries from authoritative attempt/evidence records and introducing read models only when required.
- [Educator workflow complexity] → Mitigate by separating assignment, review, grading, and feedback-release states so the workflow remains understandable.
- [Institutional expectations around grading and transcript quality] → Mitigate by making evidence provenance and auditability first-class requirements from the start.

## Migration Plan

1. Define canonical assessment entities, states, and evidence relationships.
2. Introduce assessment attempt history and educator review/grading events as additive records.
3. Wire learner and educator entry surfaces to the canonical assessment model.
4. Add mastery aggregation and progression eligibility integration on top of existing progression authority.
5. Add reporting/read-model outputs only after the authoritative records are stable.
6. Roll out with compatibility around existing progress behavior until assessment maturity is confirmed.

Rollback should preserve the existing lesson and progress systems because this design layers on top of them rather than replacing them.

## Open Questions

- How granular should mastery thresholds be by default: per objective, per assessment, or both?
- What is the initial rubric model and how much of it should be visible to learners before grading?
- Should retake policy defaults vary by assessment type, org type, or instructor-defined policy?
- Which reporting outputs are required first for institutional readiness: gradebook, transcript preview, or mastery dashboard?
