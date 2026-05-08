# Tasks

## Roadmap Framing

- [ ] Treat this change as a multi-year institutional transformation roadmap rather than a single implementation milestone
- [ ] Preserve the current lesson governance, organization, progress, curriculum hierarchy, analytics, Angular frontend, Tailwind patterns, Storybook approach, and existing lesson or shell systems wherever they are structurally sound
- [ ] Favor evolutionary architecture over broad rewrites, parallel educational systems, or disconnected operational stacks
- [ ] Sequence implementation so institutional credibility, maintainability, and platform coherence improve before large-scale feature expansion
- [ ] Use the proposal, design, and capability specs in this change as the governing framework for roadmap prioritization

---

## 1. Platform Stabilization & Foundation Hardening

### Preserve

- [ ] Preserve the current FastAPI, SQLAlchemy, organization, progress, governance, analytics, and Angular application foundations
- [ ] Preserve the canonical Course -> Unit -> Lesson -> Activity hierarchy and current lesson delivery contracts
- [ ] Preserve existing section, assignment, lesson-session, and role-aware frontend flows as the base for future institutional tooling

### Evolve

- [ ] Harden auth, session, and active-organization consistency across web flows
- [ ] Stabilize organization onboarding and post-login operational routing
- [ ] Consolidate governance ownership so lesson readiness, review, and role-based visibility remain canonical and non-duplicated
- [ ] Stabilize shell, sidebar, dashboard layout, and lesson-entry behavior across role contexts
- [ ] Improve lesson delivery reliability, session continuity, and API contract consistency
- [ ] Expand backend and frontend test coverage around auth, org context, lessons, progress, sessions, assignments, and analytics
- [ ] Strengthen seed and demo environment reliability so institutional demos reflect true platform capability

### Pressure Points

- [ ] Track route-family overlap, hidden flow coupling, and brittle session/bootstrap dependencies
- [ ] Identify API contract drift between student, teacher, and authoring surfaces
- [ ] Watch for frontend layout fixes that patch individual pages instead of shared shell behavior

### UX Priorities

- [ ] Remove layout instability, confusing auth transitions, and shell-state inconsistency
- [ ] Make first-run flows, lesson entry, and dashboard arrival states predictable and trustworthy
- [ ] Ensure role-specific surfaces feel intentional rather than partially adapted

### Governance Considerations

- [ ] Keep lesson governance centralized and reviewer-controlled
- [ ] Prevent stabilization work from bypassing existing approval, readiness, or role-boundary rules
- [ ] Document canonical ownership for auth, org, curriculum, progress, and operational state

### Scalability Concerns

- [ ] Validate that session, org switching, and API contract patterns can survive broader school and family use
- [ ] Reduce accidental complexity before more reporting, pathway, and AI layers are added

---

## 2. Academic Standardization

### Preserve

- [ ] Preserve the current lesson quality system, source-backed lesson model, readiness evaluation, and review workflow
- [ ] Preserve the existing course, unit, lesson, and activity structure as the curriculum spine

### Evolve

- [ ] Enforce lesson completeness expectations consistently across learner-facing curriculum
- [ ] Build curriculum review and educator-facing QA workflows on top of the current governance model
- [ ] Strengthen source validation, citation quality, and traceability workflows
- [ ] Audit and normalize academic metadata for age bands, standards, objectives, skills, and pathway alignment
- [ ] Add standards-alignment support without creating separate curriculum stacks
- [ ] Create educator-facing curriculum QA views for instructional quality, source health, and readiness gaps

### Pressure Points

- [ ] Monitor metadata sprawl that could make lesson authoring unusable or lesson payloads unstable
- [ ] Prevent academic-quality logic from fragmenting into separate lesson, course, and pathway validation systems
- [ ] Watch for source validation rules that are too weak for credibility or too rigid for maintainability

### UX Priorities

- [ ] Make quality expectations understandable to educators, reviewers, and curriculum operators
- [ ] Keep learner-facing lesson views focused even as academic metadata grows
- [ ] Surface instructional deficiencies clearly in authoring and review workflows

### Governance Considerations

- [ ] Extend the existing review workflow instead of creating parallel quality-control channels
- [ ] Incorporate scholar, historian, and educator review expectations into the same governance family over time
- [ ] Treat curriculum revision and periodic re-review as normal academic operations

### Scalability Concerns

- [ ] Ensure quality enforcement can scale from lesson-level checks to course and pathway-level credibility
- [ ] Plan for larger curriculum teams, more content volume, and deeper source-review demands

---

## 3. Premium UX/UI Evolution

### Preserve

- [ ] Preserve Angular, Tailwind, Storybook, the shared shell, and the current lesson-viewer direction as the frontend base
- [ ] Preserve reusable component development and shared layout ownership patterns

### Evolve

- [ ] Mature the design system into a governed educational UI framework
- [ ] Redesign dashboard experiences around institutional clarity, learner motivation, and role-specific efficiency
- [ ] Execute a mobile-first responsive overhaul across core student, educator, parent, and admin surfaces
- [ ] Raise accessibility quality toward platform-wide WCAG-aligned expectations
- [ ] Deepen the immersive lesson experience without harming focus, readability, or progress clarity
- [ ] Improve navigation, information hierarchy, and institutional trust signals
- [ ] Build student motivation systems that reinforce learning without trivializing academic rigor
- [ ] Redesign onboarding for trust, clarity, and global accessibility

### Pressure Points

- [ ] Watch for page-by-page redesign drift instead of design-system-led evolution
- [ ] Monitor dashboard complexity as more academic, cohort, and reporting data becomes visible
- [ ] Avoid visual richness that undermines readability or mobile usability

### UX Priorities

- [ ] Premium visual trust, readability, emotional safety, and reduced cognitive load
- [ ] Strong role separation with coherent shared patterns
- [ ] Mobile-first learner usability and institution-grade educator/admin clarity

### Governance Considerations

- [ ] Keep teacher-only and reviewer-only information role-gated in the UI
- [ ] Ensure design evolution does not expose governed metadata inappropriately
- [ ] Align visual trust signals with real academic and operational maturity

### Scalability Concerns

- [ ] Ensure component and theming systems can support multilingual, mobile, and institutional expansion
- [ ] Prepare the design system for denser analytics, reporting, and cross-role workflow surfaces

---

## 4. Assessment & Reporting Infrastructure

### Preserve

- [ ] Preserve the current progress model, assessment foundation, certification foundation, analytics baseline, and curriculum hierarchy
- [ ] Preserve the principle that reporting is derived from canonical learner evidence rather than a duplicate ledger

### Evolve

- [ ] Expand quizzes, formative assessments, summative assessments, projects, writing assignments, and rubric workflows
- [ ] Introduce coherent grading and educator review workflows
- [ ] Build mastery tracking as an extension of progress and assessment evidence
- [ ] Create report-card, transcript-readiness, guardian reporting, and academic-record views
- [ ] Expand educator analytics, pacing visibility, standards reporting, and intervention tooling
- [ ] Add attendance or progress verification outputs appropriate to homeschool and institutional contexts

### Pressure Points

- [ ] Prevent grading, mastery, and transcript logic from drifting into separate incompatible systems
- [ ] Watch for assessment model limitations when moving beyond auto-scored question types
- [ ] Monitor reporting-query complexity and data integrity requirements as records become institution-grade

### UX Priorities

- [ ] Clear learner progress and mastery visibility
- [ ] Low-anxiety assessment experiences with understandable outcomes
- [ ] High-trust dashboards and reports for teachers, guardians, and institutions

### Governance Considerations

- [ ] Keep assessment publishing, grading logic changes, and high-stakes evaluation inside governed workflows
- [ ] Preserve auditability for assessment attempts, grading actions, and transcript-relevant changes
- [ ] Treat academic integrity as part of normal assessment governance

### Scalability Concerns

- [ ] Plan for larger assessment volume, richer grading models, and longitudinal academic history
- [ ] Prepare reporting pipelines for school, homeschool-network, and future accreditation-oriented requirements

---

## 5. Educator Operating System

### Preserve

- [ ] Preserve the current organization roles, sections, lesson sessions, assignments, progress, analytics, and lesson-governance foundations
- [ ] Preserve teacher notes, discussion prompts, and role-aware lesson visibility as the seed of educator-facing instructional tooling

### Evolve

- [ ] Expand classroom and cohort management workflows
- [ ] Mature assignment creation, submission review, pacing oversight, and instructional sequencing
- [ ] Build educator dashboards around learner monitoring, intervention visibility, and cohort operations
- [ ] Add pacing tools, intervention workflows, and educator communication systems
- [ ] Support governed curriculum customization within explicit review boundaries
- [ ] Add educator scheduling, planning, and operational coordination aids

### Pressure Points

- [ ] Avoid creating a second classroom model disconnected from sections, assignments, and lesson sessions
- [ ] Watch for educator workflow fragmentation across dashboards, analytics, assignments, and curriculum views
- [ ] Monitor complexity as support grows for co-teachers, substitutes, homeschool instructors, and admins

### UX Priorities

- [ ] Low-friction classroom operations and quick instructional decision support
- [ ] Clear cohort visibility, intervention signals, and assignment follow-through
- [ ] Mobile and tablet usability for real-world educator work

### Governance Considerations

- [ ] Maintain clear boundaries between educator authority, reviewer authority, and curriculum publishing authority
- [ ] Keep instructional customization bounded by governed curriculum rules
- [ ] Ensure operational actions remain auditable and institutionally accountable

### Scalability Concerns

- [ ] Support multi-classroom and multi-cohort management without overwhelming educators
- [ ] Prepare educator tooling for school-scale and homeschool-network-scale operations

---

## 6. Institutional Expansion

### Preserve

- [ ] Preserve organizations as the canonical container for schools, families, pods, programs, and future partners
- [ ] Preserve the single curriculum and progress foundation across all educational modes

### Evolve

- [ ] Add stronger homeschool workflows, school or district support patterns, and organization-scaling capabilities
- [ ] Build attendance and progress verification suited to both homeschool and institution-led environments
- [ ] Expand standards mapping, academic records, and certification pathways
- [ ] Formalize transcript-ready and institution-compatible reporting structures
- [ ] Strengthen multi-org operational controls, role models, and policy visibility

### Pressure Points

- [ ] Watch for pressure to fork the product into separate homeschool and school systems
- [ ] Monitor organization-model adequacy as families, pods, schools, and partners diverge operationally
- [ ] Prevent records and standards systems from fragmenting across use cases

### UX Priorities

- [ ] Family-friendly oversight experiences
- [ ] Institution-grade administrative clarity and reporting
- [ ] Consistent learner experience regardless of organization type

### Governance Considerations

- [ ] Clarify policy ownership across organizations, families, educators, and institutional admins
- [ ] Ensure records and completion claims remain aligned with governed curriculum and assessment evidence
- [ ] Preserve review rigor as institutional stakes rise

### Scalability Concerns

- [ ] Support growth from individual orgs to multi-school, network, and partner ecosystems
- [ ] Prepare org-level controls, records, and reporting for higher administrative load

---

## 7. AI-Assisted Learning

### Preserve

- [ ] Preserve educator authority, curriculum governance, progress evidence, assessment integrity, and organization controls as the non-negotiable base for AI
- [ ] Preserve AI as augmentation, support, personalization, intervention assistance, and accessibility enhancement only

### Evolve

- [ ] Build educator copilots for planning, summarization, and intervention support
- [ ] Introduce guided tutoring, adaptive reinforcement, multilingual tutoring, and learner scaffolding
- [ ] Add intervention recommendations, pacing recommendations, and mastery-aware support
- [ ] Implement AI governance controls, review boundaries, and transparency mechanisms
- [ ] Add usage analytics, moderation, and organizational policy controls for AI-enabled workflows

### Pressure Points

- [ ] Monitor hallucination risk, source opacity, and overreach into high-stakes academic decisions
- [ ] Avoid creating a parallel AI tutoring system disconnected from governed lessons and assessments
- [ ] Watch for privacy and data-boundary violations as AI becomes more context-aware

### UX Priorities

- [ ] Emotionally supportive, low-anxiety, readable learner assistance
- [ ] Frictionless but reviewable educator support
- [ ] Clear signaling of what AI is doing, what it knows, and when educator judgment prevails

### Governance Considerations

- [ ] Require organizational and educator control over AI scope and behavior
- [ ] Keep AI-generated content reviewable before it becomes governed curriculum or assessment material
- [ ] Preserve anti-bias, cultural-responsibility, and identity-safe expectations

### Scalability Concerns

- [ ] Plan provider abstraction, bounded orchestration, and cost-aware deployment patterns
- [ ] Prepare for differential policy settings across institutions, learner ages, and regions

---

## 8. Mobile & Global Platform Expansion

### Preserve

- [ ] Preserve the core web-based educational model and canonical lesson/progress/governance structures
- [ ] Preserve mobile-first responsive evolution as the first step before native divergence

### Evolve

- [ ] Deliver stronger mobile applications or mobile-native experiences where justified
- [ ] Add offline support patterns, low-bandwidth delivery behavior, and cross-device continuity
- [ ] Expand multilingual support and internationalization infrastructure
- [ ] Improve global accessibility, diaspora discovery, and globally relevant onboarding or support workflows
- [ ] Support international usability across devices, bandwidth conditions, and learning contexts

### Pressure Points

- [ ] Watch for mobile-native ambitions that outrun the canonical curriculum and progress architecture
- [ ] Monitor content-delivery, caching, and asset-distribution needs for global scale
- [ ] Prevent localization and multilingual needs from fragmenting curriculum structure

### UX Priorities

- [ ] Phone-primary learner usability
- [ ] Readable, resilient, low-bandwidth lesson experiences
- [ ] Clear continuity between desktop, tablet, and phone learning

### Governance Considerations

- [ ] Preserve role visibility, curriculum boundaries, and review integrity across device contexts
- [ ] Ensure multilingual and global support remain aligned with Afrocentric curriculum authority

### Scalability Concerns

- [ ] Prepare infrastructure for broader regional usage, higher mobile load, and varied connectivity realities
- [ ] Plan for translation, localization, and content-distribution complexity without duplicating platforms

---

## 9. Operational & Governance Scaling

### Preserve

- [ ] Preserve the current governance family as the seed of broader institutional operational control
- [ ] Preserve analytics and organization-aware administrative foundations as the base for platform operations

### Evolve

- [ ] Build moderation systems, audit/history systems, and curriculum publishing pipelines
- [ ] Expand educator onboarding systems and institutional administration tooling
- [ ] Mature analytics pipelines and platform observability
- [ ] Strengthen content operations, review assignment, publishing controls, and revision tracking
- [ ] Improve operational reporting for institutions, curriculum teams, and platform administrators

### Pressure Points

- [ ] Watch for operational logic spreading into disconnected admin-only silos
- [ ] Monitor audit, moderation, and publishing complexity as academic and AI operations grow
- [ ] Avoid shallow observability that cannot explain institutional failures or trust issues

### UX Priorities

- [ ] Efficient institutional administration dashboards
- [ ] Clear content-publishing and moderation workflows
- [ ] Understandable audit trails and operational health visibility

### Governance Considerations

- [ ] Maintain traceability for curriculum changes, assessment revisions, AI actions, and user-role operations
- [ ] Clarify accountability across content admins, reviewers, org admins, and institutional operators
- [ ] Support policy enforcement without excessive manual burden

### Scalability Concerns

- [ ] Prepare for larger content teams, more institutions, and higher operational compliance expectations
- [ ] Build reporting and observability patterns that can support school-network and partnership scale

---

## 10. Long-Term Innovation

### Preserve

- [ ] Preserve the canonical curriculum, governance, progress, assessment, educator, and organization model as the substrate for innovation
- [ ] Preserve institutional credibility as the filter for what innovation should and should not be pursued

### Evolve

- [ ] Expand live instruction support, collaborative learning, and richer cohort participation systems
- [ ] Deepen immersive and media-rich learning
- [ ] Explore voice-assisted learning, advanced AI tutoring, and real-time learner support
- [ ] Enable institutional partnerships, museum/archive collaboration, and scholar collaboration systems
- [ ] Extend curriculum, research, and partnership workflows without fragmenting academic authority

### Pressure Points

- [ ] Watch for innovation features that bypass curriculum review, educator authority, or academic integrity
- [ ] Monitor whether immersive and collaborative systems strain mobile, accessibility, or observability foundations
- [ ] Avoid novelty investments that dilute institutional seriousness

### UX Priorities

- [ ] Innovation should deepen engagement, confidence, and cultural richness without increasing confusion
- [ ] Collaborative and media-rich experiences must remain readable, accessible, and instructionally coherent

### Governance Considerations

- [ ] New collaboration, scholar, and partner systems must inherit existing governance and review logic
- [ ] High-visibility innovation should be constrained by source quality, moderation, and institutional oversight

### Scalability Concerns

- [ ] Prepare partner and scholar workflows for distributed collaboration at scale
- [ ] Plan for heavier media, interaction, and AI loads without destabilizing the core platform

---

## Cross-Phase Execution Rules

- [ ] Validate each implementation phase against the institutional-learning-platform, afrocentric-curriculum-framework, premium-global-learning-experience, assessment-and-reporting-system, educator-operating-system, and ai-assisted-learning-and-tutoring specs
- [ ] Favor extension of current routes, models, schemas, and UI systems before adding new structural layers
- [ ] Treat architecture rewrites as last-resort responses to proven pressure points rather than roadmap defaults
- [ ] Require every major phase to improve maintainability, institutional trust, and operational clarity, not just feature breadth
- [ ] Reassess roadmap ordering after each major phase using actual implementation evidence, product maturity, and institutional readiness signals
