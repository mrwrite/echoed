## Why

EchoEd needs a rigorous institutional assessment and mastery foundation before it can credibly support homeschool, school, and college-prep use cases. The platform already has governed lesson delivery, canonical auth/org/session authority, and progress infrastructure, but it does not yet have one institutional assessment model that can support grading, mastery, evidence, and reporting without creating a parallel grading system.

## What Changes

- Define a canonical assessment architecture that covers lesson, unit, course, formative, summative, and mastery-check assessments.
- Establish governed assessment lifecycle and attempt history so every submission is auditable and institutionally credible.
- Add mastery thresholds, competency aggregation, and progression eligibility rules that flow from lesson evidence to unit and course mastery.
- Introduce educator assessment operations for assignment, review, manual grading, rubric use, cohort visibility, intervention insight, and pacing insight.
- Define learner-facing assessment delivery rules, unavailable states, feedback visibility, and mastery feedback.
- Establish reporting and institutional readiness foundations for gradebook, transcript, academic analytics, and evidence history support.
- Keep the assessment foundation aligned to the existing auth/org/session authority, course/unit/lesson hierarchy, and governed progression system.

## Capabilities

### New Capabilities
- `assessment-canonical-architecture`: canonical assessment types, scope, lifecycle, retake, and evidence rules.
- `mastery-and-academic-progression`: mastery thresholds, competency aggregation, progression eligibility, and remediation triggers.
- `academic-evidence-and-integrity`: authoritative attempts, grading auditability, submission provenance, and anti-corruption safeguards.
- `educator-assessment-operations`: assignment workflows, manual grading, rubric support, cohort visibility, intervention insight, and pacing insight.
- `student-assessment-experience`: governed learner delivery, attempt lifecycle, unavailable states, feedback visibility, and accessibility behavior.
- `reporting-and-institutional-readiness`: gradebook, transcript readiness, mastery reporting, evidence history, and academic analytics.
- `assessment-technical-alignment`: preservation of current lesson governance, progress authority, auth/org/session architecture, and non-parallel system boundaries.
- `assessment-verification-and-integrity`: deterministic state, visibility, mastery, reporting, and audit verification expectations.

### Modified Capabilities

## Impact

Affected systems include backend assessment APIs and data models, educator and learner assessment surfaces, progress/mastery integration, reporting foundations, and future transcript or institutional export pathways. This change intentionally preserves the current auth/org/session architecture and existing governed lesson delivery pipeline while adding a new institutional assessment layer on top of it.
