## Context

EchoEd already has the institutional pieces required to support learner progress responsibly: governed learner delivery, canonical auth and session authority, bounded assessment and mastery evidence, premium UX state primitives, and a flagship pathway implementation that proves the instructional model. The next maturity gap is runtime support. Learners can currently succeed, struggle, and continue, but the platform still needs a bounded support layer that turns weak mastery or hesitation into structured recovery, enrichment, encouragement, and educator awareness.

This change remains additive. It does not replace deterministic governed progression, does not alter assessment/mastery authority, and does not create AI tutoring or a second continuation engine. Instead, it defines how runtime remediation, enrichment, reinforcement, and educator awareness should be expressed within the existing governed ecosystem.

## Goals / Non-Goals

**Goals:**
- Add bounded runtime remediation continuation on top of existing governed progression and mastery evidence.
- Add bounded runtime enrichment that offers optional deeper learning without fragmenting the pathway structure.
- Define supportive learner-facing reinforcement and retry semantics that preserve dignity and momentum.
- Define remediation-aware and enrichment-aware “what’s next” guidance within the current continuation architecture.
- Add educator-visible runtime support signals without creating enterprise dashboards or workflow sprawl.
- Preserve accessibility, mobile readability, premium UX consistency, and reporting compatibility.

**Non-Goals:**
- Building AI tutoring, chat tutoring, or open-ended adaptive tutoring systems.
- Replacing the existing governed progression resolver.
- Introducing a new assessment engine, grading engine, or mastery engine.
- Building a parent portal, messaging platform, or LMS-style intervention workflow system.
- Creating unbounded branching or gamified loop mechanics.

## Decisions

1. **Runtime support is an additive layer on top of governed progression, not a new progression engine.**
   Remediation and enrichment states should influence learner guidance, educator awareness, and bounded support content, but the canonical progression backbone remains unchanged.
   - Alternative considered: a runtime continuation engine that dynamically overrides the governed lesson sequence.
   - Rejected because it would duplicate progression authority and create opaque learner-state behavior.

2. **Weak mastery signals should trigger bounded support states, not punitive gating.**
   Learners need recovery and reinforcement opportunities that preserve dignity and momentum while still preserving institutional evidence and governed availability rules.
   - Alternative considered: hard stop failure loops or repeated forced reassessment.
   - Rejected because it would increase shame, friction, and disengagement for younger learners and recovery contexts.

3. **Enrichment remains optional, bounded, and culturally grounded.**
   Deeper exploration should invite curiosity without becoming a second pathway tree or an uncontrolled branching system.
   - Alternative considered: open-ended enrichment tracks with independent sequencing.
   - Rejected because it would create branching complexity and de facto parallel runtime pathways.

4. **Learner reinforcement must be emotionally supportive, not manipulative.**
   Runtime support should use affirming language, gentle celebration, and confidence-preserving retry patterns rather than streaks, point farming, or dopamine-loop mechanics.
   - Alternative considered: a gamified reward layer to increase engagement.
   - Rejected because it conflicts with institution-grade trust and the platform’s pedagogical direction.

5. **Educator awareness should be lightweight and actionable.**
   Teachers and facilitators need visibility into remediation and enrichment state, pacing risk, and confidence risk, but not heavy new workflow systems.
   - Alternative considered: a full intervention console with workflow queues and grading actions.
   - Rejected because it would expand scope into enterprise LMS complexity.

6. **Runtime support must reuse the existing evidence and mastery foundation.**
   Support decisions should derive from current attempts, events, mastery summaries, governed lesson delivery state, and existing runtime context instead of inventing new learner-state ledgers.
   - Alternative considered: a separate runtime state store detached from assessment/mastery evidence.
   - Rejected because it would fragment reporting, learner continuity, and educator interpretation.

7. **Reporting compatibility must be preserved even before reporting UX expands.**
   Runtime support states should remain explainable from current evidence, progress state, and bounded metadata so future reporting can incorporate them without reinterpretation.
   - Alternative considered: purely ephemeral support states with no stable semantics.
   - Rejected because educators and institutions need continuity and auditability.

## Risks / Trade-offs

- [Support logic becomes a hidden second progression system] -> Mitigation: require governed progression to remain canonical and limit remediation/enrichment to guidance, bounded activities, and explicit metadata.
- [Remediation feels punitive or shaming] -> Mitigation: define emotionally safe language, gentle recovery flow, and confidence-preserving retry semantics.
- [Enrichment branches grow uncontrolled] -> Mitigation: keep enrichment optional, bounded, and modeled as additive extension content, not separate sequencing.
- [Educator visibility becomes dashboard sprawl] -> Mitigation: keep awareness lightweight and embed it into existing surfaces and metadata patterns.
- [Runtime support becomes inaccessible or cognitively heavy] -> Mitigation: require low-cognitive-load patterns, mobile-friendly layouts, and premium UX state consistency.
- [Support states become impossible to report coherently later] -> Mitigation: derive them from existing evidence, attempts, mastery summaries, and governed state.

## Migration Plan

1. Define runtime remediation, enrichment, reinforcement, continuation, educator-awareness, and accessibility rules in spec form first.
2. Identify the smallest flagship-pathway implementation slice that can operationalize runtime support without changing progression semantics.
3. Add runtime support metadata and read models additively on top of current governed delivery and assessment evidence.
4. Extend existing learner and educator surfaces using premium UX primitives rather than introducing new route families or dashboard products.
5. Add focused regression coverage for continuation consistency, runtime support semantics, educator visibility, and accessibility before expanding beyond the flagship slice.

Rollback remains low-risk at this stage because the change is planning-oriented and bounded to additive evolution. Future implementation phases should be reversible by disabling the runtime support layer while leaving governed delivery and assessment foundations untouched.

## Open Questions

- Which mastery or attempt signals should trigger remediation-aware continuation versus simple encouragement-only messaging?
- How much enrichment should be lesson-scoped versus unit-scoped before branching becomes too complex?
- What is the minimum educator-awareness surface that is useful without becoming a new intervention product?
- Which support states need durable read-model representation versus computed runtime interpretation?
- How should runtime support semantics be exposed to families or homeschool operators without creating a separate parent platform?
