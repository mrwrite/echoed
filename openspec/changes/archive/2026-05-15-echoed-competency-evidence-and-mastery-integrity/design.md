## Context

EchoEd already preserves assessment attempts and attempt events as historical evidence, supports competency alignment, derives runtime support cues, and validates historical lineage risk. Those capabilities establish evidence preservation, but they do not yet define one cross-cutting contract for when mastery interpretation remains trustworthy as assessments are revised, superseded, deprecated, or read back through staff, runtime-support, certification, and reporting surfaces.

The missing layer is not a replacement mastery engine. It is a bounded integrity layer that explains how existing mastery summaries, runtime guidance, and reporting outputs remain anchored to authoritative evidence without silently inheriting meaning from newer assessment revisions.

## Goals / Non-Goals

**Goals:**
- Preserve explainable mastery interpretation from authoritative attempts, attempt events, and competency alignments.
- Define compatible, cautionary, and incompatible assessment revision semantics for mastery and reporting interpretation.
- Detect ambiguous or unsafe mastery interpretation through read-only validation helpers and bounded visibility.
- Keep runtime remediation and enrichment guidance deterministic and grounded in safe evidence.
- Preserve certification and reporting trust without destructive evidence migration or reassignment.
- Extend staff/admin visibility with competency-evidence integrity context while keeping learner surfaces clean.

**Non-Goals:**
- Replacing the current grading engine, assessment model, or mastery-summary behavior wholesale.
- Introducing AI scoring, probabilistic grading, or a new analytics subsystem.
- Reassigning historical attempts, answers, or attempt events to successor assessment revisions.
- Replacing governed progression or changing learner delivery semantics by implication.
- Creating a workflow engine for manual compatibility adjudication in this change.

## Decisions

1. **Historical mastery remains anchored to the original evidence record.**
   Mastery interpretation must remain traceable to the exact `StudentAssessmentAttempt`, `StudentAssessmentAnswer`, `AssessmentAttemptEvent`, assessment revision, and competency alignment context that produced it.
   - Alternative considered: deriving mastery from the latest compatible assessment revision at read time.
   - Rejected because it silently changes the meaning of historical learner evidence.

2. **Assessment revision compatibility is explicit, additive, and bounded.**
   Assessment revisions should be interpretable as `compatible`, `cautionary`, or `incompatible` for mastery and reporting purposes, based on bounded lineage and alignment metadata rather than ad hoc consumer logic.
   - Alternative considered: treating any successor-linked assessment as implicitly compatible.
   - Rejected because that would hide meaningful semantic changes in prompts, scoring, competency mapping, or delivery context.

3. **Deprecated, archived, and superseded states do not destroy evidence, but they may weaken current interpretability.**
   Historical attempts remain authoritative even when an assessment becomes deprecated or superseded, but mastery, runtime support, certification, and reporting consumers must be able to detect when the surrounding revision state creates ambiguity.
   - Alternative considered: blocking all historical interpretation of deprecated or superseded evidence.
   - Rejected because that would erase valid learner history and break reporting trust.

4. **Mastery integrity is validated through read-only helpers before it is expanded into workflow behavior.**
   This initiative should start with integrity rules, warnings, and safe interpretation boundaries rather than mutation-heavy repair workflows.
   - Alternative considered: introducing automatic migration or reassignment of mastery summaries.
   - Rejected because automated repair would be high-risk and could corrupt institutional evidence trust.

5. **Runtime support uses only evidence that remains explicitly safe for continuation guidance.**
   Remediation and enrichment guidance must exclude or degrade evidence that is deprecated, archived, superseded, or revision-incompatible unless an explicit safe compatibility rule allows it.
   - Alternative considered: continuing to use any recent mastery signal regardless of revision compatibility.
   - Rejected because it could create learner recommendations from stale or semantically incompatible evidence.

6. **Staff and educator visibility stays read-only and bounded.**
   Staff/admin users may see competency-evidence integrity warnings, ambiguous mastery risks, and assessment compatibility context, but the surface must not introduce grading, reassignment, or workflow controls in this change.
   - Alternative considered: bundling manual override actions into the same visibility surface.
   - Rejected because it would conflate governance visibility with evidence mutation workflows.

7. **Certification and reporting preserve historical meaning rather than normalizing evidence into new revisions.**
   Issued certifications and historical reporting summaries should keep the competency and assessment context that actually supported them, even when newer revisions exist.
   - Alternative considered: rebuilding reporting summaries from the newest assessment lineage snapshot.
   - Rejected because it would undermine explainability and institutional trust.

8. **Technical alignment remains additive to current architecture.**
   The implementation must reuse the current assessment/mastery foundation, safe-publish validators, lineage validators, runtime-support read models, and auth/session authority without introducing a parallel mastery engine or destructive migration.
   - Alternative considered: a separate competency-evidence integrity service with duplicated evidence models.
   - Rejected because it would fragment authority and create reconciliation risk.

## Risks / Trade-offs

- [Compatibility rules may become too implicit] -> Mitigate by defining explicit compatibility classes and warning semantics in spec and code.
- [Existing mastery summaries may lack enough provenance] -> Mitigate by favoring read-only detection first and surfacing ambiguity rather than guessing.
- [Runtime support could lose useful signals when unsafe evidence is filtered] -> Mitigate by providing deterministic fallback behavior rather than inventing substitute evidence.
- [Reporting and certification consumers may interpret warnings differently] -> Mitigate by keeping issue payloads structured and historically explainable.
- [Spec overlap with prior lineage and assessment work] -> Mitigate by clearly scoping this change to mastery-integrity rules that build on, rather than replace, prior evidence-preservation guarantees.

## Migration Plan

1. Define competency-evidence anchoring and assessment revision compatibility semantics in bounded spec form.
2. Add read-only validation helpers for mastery integrity, historical ambiguity, and reporting/certification safety.
3. Reuse those validators in runtime support and staff/admin visibility surfaces without adding mutation behavior.
4. Add compatibility-aware regression coverage for assessment evidence, runtime guidance, staff visibility, certification, and reporting.
5. Keep any persistence changes additive and avoid destructive evidence migration or reassignment.

Rollback remains straightforward because the design is additive and read-only first: evidence, progression, and certification records remain in their current authoritative stores.

## Open Questions

- What minimum metadata set is sufficient to classify a successor assessment as fully compatible for mastery interpretation?
- Should mastery-integrity warnings distinguish “historically valid but cautionary” from “unsafe for runtime support” as separate severities?
- How much competency-alignment snapshot detail already exists on historical records versus needing additive read-only provenance fields later?
- Which reporting surfaces should expose integrity warnings first: staff dashboards only, exports, or certification detail views?
