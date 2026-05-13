## Context

EchoEd now has the institutional foundations needed to implement a flagship learning slice: governed learner delivery, canonical auth/session authority, institutional assessment and mastery architecture, premium UX state primitives, a multi-pathway curriculum architecture, and a flagship instructional blueprint. The missing step is a production-quality vertical slice that proves these foundations work together in practice for one pathway, one learner journey, one educator journey, and one mastery loop.

This change uses “Introduction to Africa” for K-5 as the flagship implementation pathway. The scope is deliberately bounded: 2-4 units, 3-6 lessons per unit, a small set of rich activity patterns, a lightweight but credible mastery loop, educator facilitation support, and family/community reinforcement. The goal is not broad curriculum coverage. The goal is to prove one deeply polished institutional-quality pathway that future pathways can inherit from.

This is a cross-cutting implementation because it touches curriculum structure, lesson flow, learner interactions, assessment/mastery usage, educator surfaces, family/community extensions, and UX/accessibility polish. It must preserve governed progression, avoid parallel engines, and keep institutional reporting compatibility intact.

## Goals / Non-Goals

**Goals:**
- Implement one flagship pathway vertical slice that demonstrates the canonical EchoEd instructional model end to end.
- Preserve governed learner delivery, unavailable-state semantics, assessment/mastery architecture, auth/session authority, and premium UX foundations.
- Implement a bounded set of reusable learner activity patterns and mastery interactions without proliferating activity types.
- Implement a canonical educator facilitation slice and a bounded family/community integration slice.
- Add focused regression coverage so the flagship implementation becomes a stable reference slice for future pathway work.

**Non-Goals:**
- Mass-generating curriculum content or covering all grade bands.
- Rewriting the platform, shell, lesson system, or assessment system.
- Creating a separate parent platform, educator LMS, or pathway-specific progression engine.
- Building a full institutional reporting or transcript product.
- Expanding into a full K-12 or multi-pathway rollout during this change.

## Decisions

1. **The flagship implementation will be vertically deep but horizontally narrow.**
   The pathway will cover a small number of units and lessons with high polish instead of broad curriculum breadth.
   - Alternative considered: generating a larger number of lessons with lighter implementation depth.
   - Rejected because this change is meant to prove canonical quality, not volume.

2. **Activity richness will come from a bounded canonical pattern set.**
   Reflection, discussion, geography, ecosystem, storytelling, vocabulary, multimedia, and lightweight project patterns will be implemented as canonical activity shapes rather than many bespoke interaction types.
   - Alternative considered: introducing many new custom activity engines.
   - Rejected because it would fragment the lesson system and slow institutional hardening.

3. **Assessment and mastery will remain an operationalization of current foundations.**
   The flagship pathway will use formative checks, lightweight summative moments, reflections, and discussion/project evidence while preserving current assessment architecture and reporting compatibility.
   - Alternative considered: inventing a flagship-specific mastery mechanic.
   - Rejected because it would undermine the institutional assessment foundation already established.

4. **Educator and family support will be implemented as bounded extensions of existing flows.**
   Educator visibility, pacing, facilitation support, and family/community prompts will be added without creating separate platforms or communication systems.
   - Alternative considered: building richer but isolated educator or parent products first.
   - Rejected because it would exceed the vertical-slice scope and create coordination overhead before the flagship model is proven.

5. **Premium UX polish must stay inside the current architectural primitives.**
   Lesson rhythm, accessibility, delight, and responsive refinement will extend existing primitives and page patterns rather than introducing a new shell or interaction framework.
   - Alternative considered: a dedicated flagship frontend subsystem.
   - Rejected because it would violate the evolutionary architecture strategy.

## Risks / Trade-offs

- [Vertical slice scope expands into full curriculum production] -> Mitigation: keep unit and lesson counts explicitly bounded and require reuse of canonical activity patterns.
- [Flagship interactions become too bespoke to reuse] -> Mitigation: treat every new learner interaction as a reusable canonical pattern, not a one-off feature.
- [Educator support drifts into LMS complexity] -> Mitigation: keep educator implementation focused on visibility, pacing, assignment context, and facilitation cues.
- [Family/community integration becomes an off-platform dependency] -> Mitigation: keep home/community extensions optional and lightweight.
- [UX polish introduces behavioral drift] -> Mitigation: preserve governed delivery, progression, and assessment semantics and verify them with focused regression tests.

## Migration Plan

1. Implement the flagship pathway structure and content-model boundaries first.
2. Layer canonical lesson flow and bounded learner activity patterns on top of existing lesson delivery.
3. Operationalize the assessment/mastery loop using current assessment foundations.
4. Add educator visibility and family/community support in bounded, non-parallel flows.
5. Add UX/accessibility polish and focused regression coverage across the flagship slice.
6. Use this implementation as the canonical reference for future pathway rollout planning.

Rollback should be manageable because the work is additive and bounded to a single pathway slice; existing governed delivery and assessment/runtime systems remain intact underneath.

## Open Questions

- Which activity patterns are essential in the first slice versus better deferred to later pathway phases?
- How much offline/printable family reinforcement is reasonable in the initial implementation without creating maintenance overhead?
- What is the right threshold for “production-quality” educator facilitation support in the first slice?
- How much completion celebration is appropriate before reward systems begin to feel gamified rather than affirming?
