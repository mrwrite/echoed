## Context

EchoEd already has the core institutional runtime needed for a durable curriculum architecture: governed learning delivery, canonical auth/org/session authority, the course/unit/lesson hierarchy, institutional assessment and mastery foundations, educator operating models, and a premium UX baseline. What it lacks is a long-term academic architecture that explains how these existing systems scale into one multi-pathway global learning platform without drifting into separate curriculum trees, separate progression models, or separate assessment systems.

This change is strategic and architectural. It is not a content-generation effort, not a course authoring initiative, and not a rewrite of the curriculum model. The goal is to define how one institutional system can support Afrocentric flagship experiences, core academics, STEM, financial literacy, homeschool, GED/adult education, college/career readiness, and lifelong diaspora learning while preserving governed delivery and evolutionary implementation strategy.

Stakeholders include learners, parents, homeschool operators, teachers, curriculum leads, institutional partners, community organizations, and future international or NGO deployments. The architecture must support multiple use cases without allowing each use case to fork platform authority.

## Goals / Non-Goals

**Goals:**
- Define one canonical curriculum pathway taxonomy that can represent multiple learning pathways inside the existing course/unit/lesson system.
- Clarify grade-band, sequencing, pacing, prerequisite, and cross-grade transition semantics for institutional progression.
- Make Afrocentric grounding a system-wide curricular principle that can shape all pathways rather than a separate elective domain.
- Define interdisciplinary relationships and mastery alignment rules without creating parallel learning graphs.
- Establish educator authoring, approval, publishing, and adaptation boundaries that scale across organizations and regions.
- Define learner journey architecture for multi-pathway participation, pathway discovery, cohorting, and parent or homeschool involvement.
- Preserve technical alignment with governed delivery, institutional assessment foundations, auth/session authority, and premium UX hardening.

**Non-Goals:**
- Generating or rewriting course content.
- Replacing the existing course/unit/lesson hierarchy.
- Introducing a parallel assessment, mastery, or progression engine.
- Building a new dashboard product, transcript export, or curriculum marketplace in this change.
- Redesigning the Angular shell or frontend architecture.

## Decisions

1. **Pathways are curricular overlays on the existing governed hierarchy, not a second hierarchy.**
   Pathways will organize and relate courses, units, and lessons already governed by the platform rather than replacing them with a new content tree.
   - Alternative considered: a separate pathway graph with its own lesson objects.
   - Rejected because it would split governance, delivery, and assessment authority across parallel systems.

2. **Grade-band progression remains institutionally governed through current progression foundations.**
   Grade-band and sequencing semantics should describe how curriculum is structured and recommended, but they must not replace or bypass the existing governed progression backbone.
   - Alternative considered: a new pathway-specific progression engine.
   - Rejected because it would fragment progression authority and make assessment/mastery portability harder.

3. **Afrocentric grounding is cross-cutting, not isolated to cultural or history pathways.**
   Cultural grounding, diaspora relevance, representation, and community-centered pedagogy must be expressed as curricular expectations that can shape math, science, literacy, economics, and workforce pathways.
   - Alternative considered: confining Afrocentric grounding to a flagship heritage track.
   - Rejected because it would weaken the stated educational identity of the platform.

4. **Interdisciplinary learning must be modeled through governed relationships, not ad hoc duplication.**
   Cross-disciplinary connections should be defined as canonical relationships and alignment metadata so pathway interoperability remains discoverable and assessable.
   - Alternative considered: copying similar content across subject-specific pathways.
   - Rejected because it would create curricular drift and reporting inconsistencies.

5. **Assessment and mastery alignment must extend the existing institutional assessment foundation.**
   Pathway mastery semantics, evidence expectations, and credentialing boundaries must build on the current assessment/mastery foundation rather than inventing a new pathway-specific grading system.
   - Alternative considered: pathway-local badges, completions, or informal mastery definitions.
   - Rejected because it would undermine institutional credibility and portability.

6. **Institutional and organizational customization must stay inside governed authoring boundaries.**
   Organizations may adapt pathway experiences regionally or culturally, but ownership, approval, publication, and adaptation rules must remain explicit and reviewable.
   - Alternative considered: unrestricted org-level curriculum forks.
   - Rejected because it would create quality divergence and weaken platform-wide trust.

7. **Global scalability is a first-class architecture concern, not a later retrofit.**
   Localization, low-bandwidth operation, institutional partnerships, homeschool cooperatives, and NGO or community-center deployment should shape the architecture up front.
   - Alternative considered: optimize first for one domestic K-12 mode and retrofit later.
   - Rejected because the platform vision is explicitly multi-pathway and globally scalable.

## Risks / Trade-offs

- [Too much abstraction before implementation] -> Mitigation: keep this change grounded in the existing course/unit/lesson hierarchy and define explicit boundaries for future implementation phases.
- [Pathway sprawl or taxonomy overload] -> Mitigation: define canonical ownership, discoverability, and interdisciplinary relationship rules early.
- [Afrocentric grounding becoming symbolic instead of structural] -> Mitigation: require cross-pathway curricular grounding rather than treating it as a specialty track.
- [Customization causing curricular fragmentation] -> Mitigation: keep org adaptation inside governed publishing and approval boundaries.
- [Mastery and credentialing ambiguity across pathways] -> Mitigation: defer new engines and instead extend the existing assessment/mastery foundation with clear portability and evidence requirements.
- [International scaling assumptions conflicting with current UX or infrastructure] -> Mitigation: treat localization, low-bandwidth behavior, and institutional deployment boundaries as architecture-level concerns now, implementation phases later.

## Migration Plan

1. Land the strategic curriculum architecture artifacts first: pathway taxonomy, grade-band semantics, Afrocentric grounding, interdisciplinary relationships, mastery alignment, authoring governance, learner journey, and scalability boundaries.
2. Use those artifacts to drive phased implementation planning before changing data models or APIs.
3. Introduce future curriculum metadata additively on top of existing course/unit/lesson structures rather than replacing them.
4. Extend existing assessment/mastery models for pathway alignment only after the curriculum semantics are stable.
5. Roll out educator and learner pathway experiences in bounded phases that preserve current delivery, progression, and UX foundations.

Rollback is low-risk at this stage because this change is planning-only and does not modify runtime behavior.

## Open Questions

- What is the minimum canonical pathway taxonomy that is expressive enough for long-term use without over-modeling early implementation?
- Which sequencing semantics should be institutionally normative versus configurable by organization type?
- How much regional or cultural customization should be allowed before a pathway becomes a separately governed derivative?
- What initial pathway-level credentialing boundaries are appropriate before formal transcript or institutional export work begins?
- How should lifelong diaspora learning be represented alongside age-banded academic pathways without diluting academic rigor for school-like use cases?
