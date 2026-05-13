## Context

EchoEd already has governed progression, institutional assessment/mastery foundations, and bounded runtime remediation/enrichment guidance for the flagship pathway. That runtime support is currently learner-facing and reporting-compatible, but educators still need a lightweight way to notice which learners may need support, which learners are ready for deeper extension, and which learners are progressing steadily. The existing teacher/admin dashboards, analytics read models, and premium UX primitives provide a natural place to add this without creating a separate educator product area.

## Goals / Non-Goals

**Goals:**
- Expose educator-visible runtime support state from existing continuation guidance and assessment/mastery evidence.
- Reuse existing teacher/admin dashboard architecture and analytics/reporting read models wherever possible.
- Keep educator visibility read-only, bounded, and understandable.
- Preserve learner-safe separation so educator-only hints are available only in educator/reporting contexts.
- Scope initial implementation to the Introduction to Africa flagship pathway.

**Non-Goals:**
- Building a new analytics dashboard or educator product area.
- Adding grading workflows, messaging, notifications, or assignment automation.
- Introducing intervention tasks, workflow queues, or new progression state machines.
- Expanding beyond the flagship pathway in the first slice.
- Replacing governed progression, assessment scoring, or certification semantics.

## Decisions

### 1. Reuse existing runtime continuation guidance as the support-state backbone
The implementation SHALL build educator visibility on top of the existing continuation guidance, assessment evidence summaries, and mastery summaries rather than inventing a new intervention model.

Rationale:
- This preserves one canonical runtime support interpretation.
- It avoids duplicated learner-state logic across learner and educator surfaces.

Alternative considered:
- Create separate educator-only support calculation logic. Rejected because it would drift from learner/runtime guidance and create a second support model.

### 2. Keep educator support visibility read-only and additive
Educator-facing support context SHALL be exposed as read-model data and UI summaries only. It SHALL NOT write intervention records, mutate progression, or assign actions automatically.

Rationale:
- The initiative is bounded to visibility, not workflow automation.
- This keeps the system aligned with governed progression authority.

Alternative considered:
- Add intervention tables or educator action tracking. Rejected because it expands into workflow/LMS territory prematurely.

### 3. Integrate into existing dashboard and reporting surfaces
The first implementation SHALL use current teacher/admin dashboard areas and existing analytics/reporting payloads, with optional additive support summary cards or learner-support sections.

Rationale:
- Educators already use those surfaces.
- This avoids route sprawl and a new educator navigation area.

Alternative considered:
- Create a standalone runtime support dashboard route. Rejected because it would create a new product surface without enough scope justification.

### 4. Preserve learner-safe separation explicitly in contracts
Educator-visible fields such as pacing hints, intervention hints, or support-language summaries SHALL remain educator/reporting-only and SHALL NOT be exposed through learner-facing student-course payloads unless already intended for learner use.

Rationale:
- Confidence-support context often contains facilitation-oriented framing that is not meant for learners.
- This avoids accidental leakage of staff-only interpretation.

Alternative considered:
- Use one fully shared payload for both learner and educator contexts. Rejected because it weakens field-boundary safety.

### 5. Scope the first slice to flagship-pathway evidence and metadata
Runtime support visibility SHALL initially target the seeded Introduction to Africa pathway, using its existing remediation/enrichment metadata and current assessment/mastery evidence.

Rationale:
- The flagship pathway already proves the continuation guidance loop.
- This keeps implementation bounded and testable.

Alternative considered:
- Generalize to every course immediately. Rejected because many courses do not yet carry comparable runtime support metadata.

## Risks / Trade-offs

- [Educator surfaces become too dense] -> Keep the first slice to lightweight cards, badges, and summaries with existing state primitives instead of deep tables or analytics panels.
- [Learner-safe and educator-only fields drift] -> Centralize derivation in existing analytics/read-model code and add focused tests for field separation.
- [Support-state interpretation gets duplicated] -> Reuse the existing continuation guidance backbone and avoid standalone educator-only state logic.
- [Flagship-only heuristics are mistaken for universal policy] -> Mark the scope explicitly in specs, tasks, and tests, and keep the initial implementation pathway-scoped.

## Migration Plan

1. Extend existing read models and schemas additively for educator support visibility.
2. Add educator UI summaries to existing teacher/admin dashboard surfaces with canonical loading, empty, error, and retry states.
3. Add focused backend and frontend regression coverage for support visibility, learner-safe separation, and no progression mutation.
4. Roll back by removing additive fields and UI summaries if necessary; no data migration or destructive change is required.

## Open Questions

- Which existing teacher/admin surface should be the canonical first home for learner runtime support summaries: top-level dashboard cards, course-level tables, or both?
- Should educator visibility distinguish "normal continuation" learners visually, or only surface remediation/enrichment learners plus an aggregate count?
- How much educator-facing support language should be shown inline versus behind a lightweight expandable detail view?
