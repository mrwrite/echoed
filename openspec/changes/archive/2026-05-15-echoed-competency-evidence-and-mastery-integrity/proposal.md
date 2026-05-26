## Why

EchoEd now has foundational assessment attempts, attempt events, competency alignment, runtime support, curriculum lineage, safe-publish validation, and staff lineage visibility. What it still lacks is one bounded integrity layer that defines when mastery remains trustworthy, explainable, and historically safe as assessments evolve. Without that layer, the platform risks ambiguous mastery inheritance, runtime guidance based on unsafe evidence, and certification or reporting summaries that silently mix incompatible evidence.

## What Changes

- Define competency-evidence anchoring rules so mastery summaries remain explainable from assessment attempts, attempt events, and competency alignments.
- Define assessment revision compatibility classes and interpretation rules for deprecated, archived, superseded, and successor-linked assessments.
- Add bounded historical mastery-safety validation so ambiguous or unsafe mastery interpretation can be detected without mutating evidence.
- Align runtime remediation and enrichment guidance with valid mastery evidence and deterministic evidence guardrails.
- Expose competency-evidence and mastery-integrity warnings through read-only staff/admin visibility surfaces.
- Preserve certification and reporting trust by preventing silent mixing or reassignment of incompatible historical evidence.
- Keep the work additive to existing assessment, reporting, governed delivery, and lineage validators rather than introducing a new grading or mastery engine.

## Capabilities

### New Capabilities
- `competency-evidence-anchoring`: evidence anchoring, explainability, and historical competency context rules.
- `assessment-revision-compatibility-integrity`: compatible vs incompatible revision semantics for mastery interpretation.
- `historical-mastery-safety`: read-only detection of ambiguous mastery interpretation across curriculum evolution.
- `runtime-support-evidence-integrity`: runtime remediation and enrichment guardrails for unsafe or incompatible evidence.
- `staff-competency-integrity-visibility`: read-only staff/admin visibility for competency-evidence and mastery-integrity risks.
- `certification-reporting-evidence-integrity`: historical certification and reporting explainability for mastery-backed evidence.
- `competency-mastery-technical-alignment`: additive architecture boundaries for competency evidence and mastery integrity work.
- `competency-mastery-verification`: focused regression expectations for traceability, compatibility, runtime support, and reporting preservation.

### Modified Capabilities
- `assessment-compatibility`: extend compatibility semantics from evidence preservation to mastery interpretation safety.
- `assessment-evidence-and-mastery-safety`: extend evidence preservation rules with competency-backed mastery integrity and ambiguity detection.
- `educator-runtime-support-visibility`: ensure educator/runtime support stays grounded in safe mastery evidence.
- `staff-lineage-safety-visibility`: extend staff visibility with mastery-integrity and competency-evidence warning context.
- `certification-and-reporting-revision-safety`: preserve certification and reporting trust when competency evidence spans revisions.

## Impact

Affected systems include backend assessment/mastery validators, runtime support evidence selection, certification and reporting read models, and bounded staff/admin visibility surfaces. This change is intentionally evolutionary: it preserves existing `Assessment`, `Question`, `StudentAssessmentAttempt`, `StudentAssessmentAnswer`, `AssessmentAttemptEvent`, competency alignment, governed delivery, safe-publish validation, and lineage architecture while adding integrity rules, warnings, and verification around them.
