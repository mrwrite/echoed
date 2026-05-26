## Why

EchoEd now has additive curriculum governance foundations for lesson readiness, course publish readiness, and bounded staff visibility, but it still lacks a canonical model for safe curriculum revision and republishing over time. As more flagship and multi-pathway curriculum assets move from draft to published use, the platform needs clear rules for revision metadata, published replacement behavior, archival, and learner-safety guarantees without rewriting the curriculum model or creating a second publishing engine.

This change defines how curriculum can evolve safely after publication while preserving governed learner delivery, historical assessment evidence, mastery reporting, runtime support context, and existing learner progress continuity.

## What Changes

- Define additive curriculum revision metadata and lineage expectations for pathway, course, unit, lesson, and related assessment compatibility.
- Define safe published editing rules that distinguish minor updates from material changes and preserve learner continuity during republish operations.
- Define archival and deprecation safeguards that protect learner progress, assessment attempts, mastery evidence, certifications, and runtime support evidence.
- Define draft revision workflow expectations for staff preview, reviewer visibility, publish replacement semantics, and bounded rollback rules.
- Define assessment compatibility rules for curriculum changes so historical evidence remains trustworthy when aligned content evolves.
- Define bounded staff/admin UX and governance expectations for readiness warnings, revision summaries, and learner-safe messaging.
- Preserve the existing Course, Unit, Lesson, Assessment, lesson governance, governed delivery, and auth/session architecture while keeping all versioning behavior additive and evolutionary.

## Capabilities

### New Capabilities
- `curriculum-version-metadata`: additive revision metadata, lineage semantics, and safe current-version references across the existing curriculum hierarchy.
- `safe-published-editing`: rules for minor versus material edits, safe republish boundaries, and learner continuity preservation.
- `historical-learner-safety`: guarantees for learner progress, assessment attempts, mastery evidence, certifications, and runtime support evidence during curriculum evolution.
- `draft-revision-workflow`: bounded draft revision, review visibility, publish replacement, preview, and rollback expectations without a full CMS rewrite.
- `assessment-compatibility-under-revision`: compatibility rules for assessment evidence preservation when curriculum revisions affect aligned content.
- `curriculum-versioning-ux-boundaries`: staff/admin-only visibility, revision warnings, learner-safe messaging, and bounded governance surfaces.
- `curriculum-versioning-technical-alignment`: technical guardrails that preserve the current curriculum model, governed delivery, runtime support, and assessment/mastery architecture.

### Modified Capabilities

## Impact

This change affects curriculum governance policy, future staff publishing flows, assessment compatibility expectations, and historical learner-safety guarantees. It is intentionally bounded: it does not introduce git-style version control, branching curriculum trees, a second curriculum engine, destructive migrations, or new learner progression semantics.
