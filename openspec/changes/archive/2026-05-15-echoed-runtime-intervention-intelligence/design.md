## Context

EchoEd already has several bounded systems that this change must build on rather than replace: governed learner continuation, runtime remediation and enrichment guidance, educator runtime support visibility, competency evidence integrity, assessment/mastery safety, historical lineage safety, and staff governance visibility. Today those systems expose useful signals, but they do not yet define one normalized intervention-intelligence layer that educators can interpret consistently across reteach, review, enrichment, monitoring, and normal continuation decisions.

The current architecture already constrains the right shape of the solution. Runtime support is read-only and additive. Competency and mastery integrity helpers already distinguish valid, explainable, ambiguous, and historically unsafe evidence. Staff visibility already uses bounded read models and premium UX state primitives. Governed delivery already owns learner progression and continuation determinism. The new change therefore has to remain a thin interpretive layer over existing evidence, not a new behavioral engine.

Stakeholders include educators who need clearer support recommendations, staff/admin users who need safe visibility, and learners whose dignity, determinism, and progression safety must not be degraded by educator-facing intelligence.

## Goals / Non-Goals

**Goals:**
- Define deterministic recommendation states for `reteach`, `review`, `enrichment`, `monitor`, and `normal`.
- Require every recommendation to cite bounded evidence basis and confidence/caution context.
- Reuse existing competency integrity and mastery safety outputs so unsafe or ambiguous evidence is either filtered out or downgraded with caution.
- Expose recommendations through existing educator/runtime visibility surfaces as read-only guidance only.
- Preserve governed learner delivery, continuation determinism, and all existing progression/scoring/certification/reporting authority.
- Add focused regression coverage for recommendation semantics and read-only guarantees.

**Non-Goals:**
- No AI-generated interventions, tutoring, messaging, or freeform recommendation text.
- No automatic assignment, intervention workflow engine, or task orchestration.
- No new grading, scoring, certification, reporting, or progression engine.
- No learner-facing mutation, labeling, behavioral prediction, or ability prediction.
- No destructive migration or replacement of existing runtime support read models.

## Decisions

### 1. Runtime intervention intelligence will be derived from existing governed evidence, not new evidence collection
The recommendation layer should consume already-authoritative signals: recent attempts, attempt events, mastery summaries, competency integrity results, runtime remediation/enrichment signals, and historical revision safety. This keeps the system deterministic and auditable.

Why this over a new signal pipeline:
- Existing evidence already has governance and safety boundaries.
- A new intervention-specific evidence model would duplicate authority and drift from mastery/reporting semantics.
- Read-only derivation preserves trust and minimizes mutation risk.

Alternative considered:
- Create a separate intervention evidence store. Rejected because it would create a second interpretation system for the same learner evidence.

### 2. Recommendation outputs will be normalized into a small bounded state model
The design should use a compact recommendation taxonomy: `reteach`, `review`, `enrichment`, `monitor`, and `normal`, plus evidence-basis fields and caution/confidence fields.

Why this over freeform or highly granular recommendation categories:
- Educators need explainable operational guidance, not opaque complexity.
- A bounded taxonomy is easier to test, govern, and keep tone-safe.
- It reduces workflow sprawl and prevents the system from becoming a shadow intervention engine.

Alternative considered:
- Allow arbitrary recommendation types per pathway or curriculum area. Rejected because it weakens determinism and complicates governance.

### 3. Competency/mastery integrity results will act as a recommendation gate, not just a display annotation
If evidence is invalid, unsafe, deprecated/superseded without safe compatibility, or ambiguous, the recommendation layer should exclude that evidence or downgrade the output with explicit caution flags.

Why this over simply displaying an integrity warning beside unchanged recommendations:
- Unsafe evidence should not quietly drive educator guidance.
- Competency integrity work already established valid/explainable boundaries that should influence downstream interpretation.
- This preserves historical evidence trust while preventing misleading confidence.

Alternative considered:
- Keep intervention logic independent of integrity helpers and show caution after the fact. Rejected because it would still allow unsafe signals to influence recommendations.

### 4. Educator visibility will extend existing runtime support surfaces rather than create a separate intervention product area
The UI/API footprint should remain within current educator runtime visibility or staff governance surfaces, using existing read-only state patterns and permission boundaries.

Why this over a dedicated intervention dashboard or workflow area:
- Existing surfaces already host bounded educator support visibility.
- A separate surface would imply a broader operational workflow the user explicitly does not want.
- Reuse keeps UX aligned with current premium primitives and authority boundaries.

Alternative considered:
- Add a standalone intervention workspace. Rejected because it encourages workflow sprawl and implicit assignment semantics.

### 5. Confidence and caution framing will be bounded, non-predictive, and evidence-derived
The design should distinguish between a confident recommendation backed by safe evidence and a cautionary recommendation where ambiguity, sparse evidence, or historical compatibility limits apply. These flags should describe evidence quality, not learner ability or likely future behavior.

Why this over predictive scoring or hidden confidence heuristics:
- The product explicitly excludes behavior prediction and AI-style inference.
- Evidence-derived caution is explainable and consistent with integrity guardrails.
- It supports educator judgment without overstating system certainty.

Alternative considered:
- Use opaque confidence scores or risk scoring. Rejected because they are harder to explain and drift toward prediction systems.

## Risks / Trade-offs

- **[Risk] Recommendation categories may overlap with existing remediation/enrichment semantics** → Mitigation: keep recommendation taxonomy explicitly aligned to current runtime support states and define only additive distinctions such as `reteach`, `review`, and `monitor`.
- **[Risk] Integrity filtering could remove too much evidence and reduce recommendation usefulness** → Mitigation: support cautionary outputs when evidence is ambiguous, rather than forcing either full confidence or no output in all cases.
- **[Risk] Staff surfaces could accidentally imply workflow authority** → Mitigation: keep all surfaces read-only, avoid action controls, and explicitly prohibit assignment, publish, grading, messaging, or intervention workflow affordances.
- **[Risk] Historical revision safety rules may be difficult for educators to interpret** → Mitigation: require concise evidence-basis and caution fields that explain whether a recommendation is grounded in safe current evidence, historically compatible evidence, or ambiguous evidence.
- **[Risk] Cross-cutting reuse could increase implementation coupling across runtime support and integrity helpers** → Mitigation: implement a narrow aggregation/helper layer that consumes existing read models instead of spreading recommendation logic across many call sites.

## Migration Plan

No destructive migration is expected. The implementation should roll out as additive read-only behavior in this order:

1. Define normalized intervention recommendation structures and helper semantics.
2. Integrate competency/mastery integrity gating into recommendation derivation.
3. Extend educator-facing read models and staff surfaces with read-only recommendation visibility.
4. Add focused regression coverage verifying non-mutation and non-regression across progression, scoring, certification, and reporting.

Rollback strategy:
- Remove or disable the additive recommendation helper and its read-only visibility surface.
- Preserve all existing runtime support, governed delivery, and learner progression behavior because no mutation path should depend on intervention intelligence.

## Open Questions

- Should `monitor` represent sparse/low-confidence evidence separately from `normal`, or only when a caution flag is present?
- Should evidence-basis output be standardized as compact codes plus human-readable explanations, or explanation-only text?
- Should the first implementation remain flagship/pathway-scoped like earlier runtime support visibility, or be generalized to any course where existing evidence relationships are safe?
