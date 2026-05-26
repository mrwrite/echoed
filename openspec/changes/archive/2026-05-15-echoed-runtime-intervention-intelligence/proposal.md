## Why

EchoEd already has governed continuation, runtime remediation/enrichment guidance, educator runtime visibility, and competency/mastery integrity safeguards, but it does not yet define one bounded intervention-intelligence layer that turns those existing signals into educator-facing reteach, review, enrichment, monitor, and normal recommendations. This change is needed now to give educators clearer, explainable, and historically safe support guidance without introducing AI tutoring, workflow automation, or a new progression engine.

## What Changes

- Define deterministic educator-facing runtime intervention recommendation semantics derived from existing governed evidence.
- Add bounded recommendation states for `reteach`, `review`, `enrichment`, `monitor`, and `normal` continuation.
- Require every recommendation to include an evidence basis and confidence/caution framing that explains why the recommendation exists.
- Add integrity guardrails so runtime intervention intelligence uses only valid and explainable mastery evidence where available and surfaces caution when evidence is ambiguous or historically unsafe.
- Extend educator-facing runtime visibility with read-only intervention intelligence, while prohibiting automatic assignments, messaging tasks, grading actions, or workflow orchestration.
- Preserve learner continuation determinism and governed delivery semantics by keeping intervention intelligence additive to existing learner-state and runtime-support read models.
- Add focused regression coverage for recommendation categories, evidence basis, caution flags, read-only behavior, and non-mutation guarantees across progression, scoring, certification, and reporting.

## Capabilities

### New Capabilities
- `runtime-intervention-recommendation-semantics`: Defines deterministic, read-only educator recommendation states and evidence-basis semantics for reteach, review, enrichment, monitor, and normal continuation.
- `runtime-intervention-evidence-guardrails`: Defines how competency integrity, mastery safety, and historical revision safety constrain runtime intervention recommendations.
- `educator-runtime-intervention-intelligence`: Defines how authorized educators receive read-only runtime intervention intelligence without assignment, messaging, grading, or workflow controls.
- `runtime-intervention-intelligence-verification`: Defines focused verification expectations for recommendation outputs, caution flags, and non-mutation behavior.

### Modified Capabilities
- `educator-read-only-intervention-awareness`: Extend existing educator intervention awareness requirements so bounded recommendation categories and evidence-basis semantics are explicitly defined.
- `runtime-support-evidence-integrity`: Extend runtime support integrity rules so intervention recommendations inherit the same valid/explainable evidence constraints and ambiguity handling.

## Impact

- Affected backend areas will likely include existing runtime support and educator visibility read helpers, competency integrity helpers, and staff-facing analytics or dashboard read models.
- Affected frontend areas will likely include existing teacher/admin runtime support surfaces and shared read-only UX primitives.
- No new AI dependency, workflow engine, grading engine, progression engine, or destructive data migration is expected.
- Auth/session authority, governed learner delivery, existing assessment/mastery architecture, and current reporting/certification semantics must remain unchanged except for new additive read-only recommendation visibility.
