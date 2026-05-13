## Context

EchoEd already has additive revision metadata, publish-readiness validation, safe-publish validation, governed learner delivery, assessment/mastery evidence, runtime support guidance, and bounded staff governance visibility. What it still lacks is a canonical historical interpretation layer for published curriculum once newer revisions exist. Without that layer, future revisions risk creating ambiguity around which curriculum record historical learner progress, assessment attempts, mastery summaries, certifications, and runtime support evidence actually reference.

This change stays inside the current institutional architecture. It must preserve the existing `Course`/`Unit`/`Lesson`/`Assessment` model family, keep governed delivery authoritative for active learner experiences, and avoid destructive migrations, branching curriculum trees, or a second curriculum engine. The main stakeholders are curriculum administrators, reviewers, reporting consumers, and learners whose historical evidence must remain trustworthy while content evolves.

## Goals / Non-Goals

**Goals:**
- Introduce bounded lineage metadata expectations for curriculum and assessment entities without replacing the current model.
- Define how superseded and successor revisions remain historically interpretable for reporting, staff visibility, and learner-safety guarantees.
- Preserve `StudentCourse`, `StudentUnitProgress`, `SegmentProgress`, assessment attempts, mastery evidence, runtime support evidence, and certifications without silent reassignment.
- Define read-only safety validation and staff/admin visibility expectations that build on current governance and safe-publishing foundations.
- Keep the implementation evolutionary so future publish workflows can rely on these guarantees without requiring a rewrite.

**Non-Goals:**
- Implement a publish, republish, rollback, or unpublish workflow.
- Introduce git-style branching, merge semantics, or a CMS-like revision tree.
- Replace governed learner delivery with a lineage-aware progression engine.
- Rewrite historical learner records to point at newer revisions automatically.
- Add learner-facing revision controls or staff editing workflows in this change.

## Decisions

### Decision: Use additive self-referential lineage metadata rather than parallel history tables

The safest evolutionary path is to add bounded predecessor/successor metadata to existing curriculum entities instead of introducing separate history tables or a new revision engine. This keeps current IDs, relations, serializers, and governance helpers usable while allowing staff and reporting surfaces to understand historical lineage explicitly.

Alternatives considered:
- Separate lineage tables: rejected because they create a parallel curriculum interpretation system and raise join complexity across governed delivery and reporting.
- External revision registry: rejected because it fragments authority away from the existing curriculum models and complicates safe-publish validation.

### Decision: Preserve historical learner and assessment records as anchored to their original entity IDs

Historical learner progress, attempts, answers, events, mastery evidence, certifications, and runtime support signals SHALL remain attached to the curriculum and assessment records they were created against. Successor relationships can provide interpretive context, but they must not trigger silent reassignment of historical records to newer revisions.

Alternatives considered:
- Auto-repoint progress or attempts to current revisions: rejected because it corrupts historical meaning and can distort reporting and credential interpretation.
- Clone historical evidence into successor revisions: rejected because it duplicates authoritative records and introduces grading ambiguity.

### Decision: Govern active delivery through current safe content while exposing lineage as read-only context

Governed learner delivery should continue to use current safe content and existing availability rules. Historical lineage is primarily a read-model and governance concern: it explains relationships, warnings, and compatibility, but it does not create a new runtime progression path or learner-facing revision selector.

Alternatives considered:
- Let learners choose older revisions: rejected because it introduces a parallel delivery mode and complicates progression integrity.
- Deliver superseded revisions automatically to learners with historical progress: rejected because it creates runtime branching and undermines current governed delivery expectations.

### Decision: Treat deprecation and rollback as bounded interpretation states, not destructive actions

Deprecation, archival, rollback, and successor visibility must be modeled as safe interpretive states. Deprecated or archived revisions may remain historically visible for staff, reporting, and evidence interpretation, but they must not imply destructive replacement or cleanup of learner records.

Alternatives considered:
- Hard removal of deprecated revisions: rejected because it risks orphaning historical progress and evidence.
- Full rollback workflow in this change: rejected because the goal is to establish safety contracts first, not staff workflow execution.

### Decision: Keep staff/admin visibility lightweight and aligned with existing governance surfaces

Lineage and historical-safety context should appear through existing staff/admin governance and course-management surfaces, backed by read-only contracts and warnings. This keeps visibility useful without expanding into a full authoring suite.

Alternatives considered:
- Dedicated lineage dashboard: rejected because it adds product surface area before the underlying safety contracts are fully exercised.
- No staff visibility until a full workflow exists: rejected because safe interpretation requires operational visibility before workflow expansion.

## Risks / Trade-offs

- [Lineage metadata can become internally inconsistent] → Mitigation: define strict default semantics, bounded validation rules, and warning/blocking behavior for invalid predecessor/successor relationships.
- [Historical titles and metadata may diverge from current course naming] → Mitigation: preserve historical labels on original records and expose successor context read-only instead of rewriting old records.
- [Safe-publish and reporting rules could become over-conservative] → Mitigation: distinguish blocking corruption risks from non-blocking interpretive warnings so staff can inspect issues without disrupting current delivery.
- [Future workflow expectations may pressure this design into branching behavior] → Mitigation: explicitly constrain lineage to interpretation and safety, not learner runtime branching or publish orchestration.
- [Adding lineage across Course, Unit, Lesson, and Assessment may increase cross-entity complexity] → Mitigation: phase implementation from metadata defaults to validation to read-only visibility, with regression coverage around no-mutation guarantees.

## Migration Plan

1. Add additive lineage metadata with backward-compatible defaults and no required rewrites of existing records.
2. Extend governance validators so safe-publish and historical-safety checks can reason about predecessor/successor relationships.
3. Extend reporting and staff/admin read models with lineage and safety context while keeping learner-safe serialization unchanged.
4. Add regression coverage proving that governed delivery, learner progress, attempts, mastery evidence, runtime support signals, and certifications remain stable.
5. Defer workflow actions such as publish replacement, rollback execution, and archive operations until the lineage contracts are proven.

Rollback strategy:
- Because the change is additive, rollback should consist of disabling or hiding lineage-aware validation and read-model usage rather than rewriting learner or curriculum records.
- Historical learner and evidence records remain authoritative regardless of whether lineage-aware staff visibility is enabled.

## Open Questions

- Whether lineage metadata should allow only one direct predecessor or support a more flexible but still bounded successor chain.
- Whether `Assessment` lineage should always track independently from `Lesson` lineage or allow explicit compatibility linkage when lesson revisions are minor.
- How much historical title and metadata snapshotting should live on learner-facing records versus being resolved through read-only reporting joins.
- Whether staff visibility for lineage warnings belongs first in existing course management surfaces, governance endpoints, or reporting summaries.
