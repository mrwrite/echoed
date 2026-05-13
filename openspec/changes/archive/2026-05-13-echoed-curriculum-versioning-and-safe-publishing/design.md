## Context

EchoEd now has baseline curriculum governance in place: academic readiness validation, lesson approval boundaries, staff-facing publish-readiness inspection, governed learner delivery, assessment/mastery foundations, runtime support read models, and flagship curriculum seeding. Those pieces are necessary but not sufficient for long-term institutional publishing. Once published curriculum begins evolving over time, the platform needs an explicit answer to a core question: how can staff revise curriculum safely without breaking learner continuity or corrupting historical evidence?

This change is not a new curriculum engine. It defines additive versioning and safe-publishing semantics on top of the existing Course, Unit, Lesson, Activity, Source, and Assessment structures. The purpose is to establish stable rules for revision metadata, safe replacement, archival, preview, compatibility, and learner-safety boundaries before a larger authoring workflow appears.

Stakeholders include curriculum leads, reviewers, teachers, admins, learners, institutional partners, and future multi-pathway content operators. The design must preserve trust for both active learners and staff maintaining curriculum over time.

## Goals / Non-Goals

**Goals:**
- Define additive revision metadata and lineage expectations that can coexist with the current curriculum model.
- Define safe published editing rules that preserve governed learner delivery and historical evidence.
- Clarify how draft revisions, publish replacement, archival, and bounded rollback should behave.
- Preserve assessment/mastery integrity, certification integrity, runtime support evidence, and learner progress continuity.
- Define bounded staff/admin visibility and warning expectations without building a full CMS or workflow suite.

**Non-Goals:**
- Rewriting Course, Unit, Lesson, or Assessment models into a new versioned content engine.
- Introducing branching curriculum trees or git-style merge semantics.
- Replacing governed progression, governed delivery, or runtime support architecture.
- Building a full authoring UI, public creator platform, or parallel publishing database in this change.
- Introducing destructive migration behavior that rewrites historical learner records.

## Decisions

1. **Versioning is additive metadata over the existing curriculum hierarchy.**
   Revision behavior must layer on top of current pathway, course, unit, lesson, and assessment structures rather than replacing them with a separate versioned content tree.
   - Alternative considered: a separate revision database or parallel curriculum tables.
   - Rejected because it would split governance authority and create migration risk across learner delivery and assessment evidence.

2. **Published editing must distinguish minor from material changes.**
   Safe evolution depends on knowing whether a change is continuity-preserving or materially instructional.
   - Minor changes: typo fixes, formatting, source metadata cleanup, non-semantic teacher guidance refinement.
   - Material changes: reordered learner flow, changed lesson expectations, altered assessment meaning, removed required content, or changed evidence-bearing instructional intent.
   - Alternative considered: treating every edit identically.
   - Rejected because it would either overconstrain harmless maintenance or underprotect learner continuity.

3. **Historical learner evidence is immutable even when published curriculum evolves.**
   Assessment attempts, mastery evidence, certifications, runtime support evidence, and progression records must remain anchored to the learner experience that actually occurred.
   - Alternative considered: mutating old evidence to follow the newest curriculum revision.
   - Rejected because it would undermine academic trust and reporting integrity.

4. **Republish behavior must preserve governed learner continuity.**
   New published revisions may become the canonical current version for future learner delivery, but in-flight or historical learner states must remain safe and interpretable.
   - Alternative considered: hard-overwriting all active and historical references to the latest content.
   - Rejected because it risks orphaned progression states and misleading evidence interpretation.

5. **Draft revision workflow remains bounded and staff-facing.**
   Draft revisions, preview, reviewer visibility, and publish replacement semantics should exist conceptually without requiring a full workflow engine in this change.
   - Alternative considered: deferring all revision semantics until a full authoring suite exists.
   - Rejected because safe publishing rules need to exist before the UI and workflow scale up.

6. **Assessment compatibility is governed, not inferred ad hoc.**
   When curriculum revisions touch lessons or assessments, the system needs explicit compatibility expectations so evidence preservation stays trustworthy.
   - Alternative considered: allowing assessment alignment drift without compatibility rules.
   - Rejected because it risks grading corruption, misleading mastery summaries, and certification ambiguity.

7. **Archival and deprecation must favor learner safety over deletion.**
   Curriculum that is no longer current should be deprecated or archived through safe references and warnings, not destructive removal.
   - Alternative considered: deleting superseded curriculum or detached records.
   - Rejected because it can orphan learner evidence and break auditability.

## Risks / Trade-offs

- [Revision semantics become too abstract] -> Mitigation: keep the change grounded in current Course/Unit/Lesson/Assessment structures and staff/admin-only governance use cases.
- [Minor versus material distinctions become inconsistent] -> Mitigation: define canonical examples and require explicit governance interpretation instead of ad hoc staff judgment.
- [Historical safety requirements slow future authoring features] -> Mitigation: accept bounded implementation complexity now to avoid learner-data corruption later.
- [Versioning grows into a parallel engine] -> Mitigation: require additive metadata and current-version references only, with no branch trees or second hierarchy.
- [Assessment alignment under revision becomes ambiguous] -> Mitigation: define compatibility expectations before implementing richer publish tooling.
- [Preview and rollback semantics become overbuilt] -> Mitigation: keep them bounded to staff/admin governance needs rather than CMS-grade workflow automation.

## Migration Plan

1. Define additive revision metadata, lineage rules, and current-version semantics for the existing curriculum hierarchy.
2. Define safe publish and republish boundaries, including minor/material change interpretation and learner continuity expectations.
3. Define archival, deprecation, and historical evidence preservation rules before broader authoring UI or workflow expansion.
4. Extend publish-readiness and staff/admin governance surfaces in later phases using these rules rather than inventing local publish behavior.
5. Introduce any future runtime implementation additively, preserving governed delivery, assessment/mastery, runtime support, and auth/session authority.

Rollback is low-risk at this stage because the change is architectural and governance-oriented. It defines bounded expectations before any destructive runtime behavior exists.

## Open Questions

- What minimal revision metadata is sufficient for institutional safety without effectively recreating source control inside the application?
- Which material changes should require replacement-versus-revision semantics rather than minor republish behavior?
- How should active learners tied to a superseded published lesson be represented if the course becomes deprecated but not deleted?
- What compatibility signal is required when a lesson revision changes associated assessment intent but not the assessment object itself?
- How much rollback should be supported operationally before it becomes indistinguishable from branching curriculum maintenance?
