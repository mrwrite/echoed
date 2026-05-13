## Why

EchoEd now has additive curriculum revision metadata and bounded readiness and safe-publish validation, but it still lacks a canonical way to interpret historical curriculum relationships once newer revisions exist. This change is needed now to guarantee learner progress, assessment evidence, mastery summaries, runtime support signals, and certifications remain trustworthy as published curriculum evolves over time.

## What Changes

- Define additive historical lineage metadata expectations for `Course`, `Unit`, `Lesson`, and `Assessment`, including safe predecessor and successor references where they can be introduced without rewriting the current model.
- Define how superseded and successor curriculum revisions remain interpretable for staff and reporting while governed learner delivery continues to use current safe content.
- Define learner progress safety rules so `StudentCourse`, `StudentUnitProgress`, and `SegmentProgress` remain valid when older curriculum revisions have successors.
- Define assessment evidence and mastery safety rules so attempts, answers, events, and competency evidence remain historically unambiguous across curriculum revisions.
- Define certification and reporting safety expectations so issued credentials and historical summaries remain interpretable after curriculum updates.
- Define bounded rollback, archival, and deprecation interpretation without destructive replacement or a new publish workflow.
- Define read-only staff/admin visibility expectations for lineage and historical safety warnings without creating a CMS workflow or learner-facing revision system.
- Preserve the existing governed delivery, assessment/mastery, runtime support, and curriculum governance architecture as the authoritative institutional system.

## Capabilities

### New Capabilities
- `historical-lineage-metadata`: Add bounded lineage metadata expectations for curriculum and assessment entities.
- `superseded-revision-interpretation`: Define how superseded curriculum remains interpretable after newer safe revisions exist.
- `learner-progress-safety-across-revisions`: Preserve learner progress integrity across curriculum revision changes.
- `assessment-evidence-and-mastery-safety`: Preserve assessment evidence and mastery interpretation across revisions.
- `certification-and-reporting-revision-safety`: Preserve certification and reporting integrity across curriculum revisions.
- `rollback-and-deprecation-boundaries`: Define bounded rollback, archival, and deprecation safety semantics.
- `staff-lineage-safety-visibility`: Expose lineage and safety context read-only for staff/admin users.
- `historical-lineage-technical-alignment`: Preserve technical alignment with the current governed curriculum architecture.
- `historical-lineage-safety-verification`: Verify lineage defaults, historical safety, and no learner-state corruption.

### Modified Capabilities
- `curriculum-version-metadata`: Extend revision metadata expectations to account for safe historical lineage references and defaults.
- `historical-learner-safety`: Extend learner-safety requirements so historical progress and evidence remain interpretable when superseded revisions exist.
- `assessment-compatibility`: Extend assessment compatibility requirements for historical revision interpretation without grading ambiguity.

## Impact

Affected areas include backend curriculum models and schemas, governance and validation helpers, reporting and runtime-support read models, staff/admin read-only visibility surfaces, and regression coverage for learner progress, evidence preservation, certification safety, and governed delivery compatibility.
