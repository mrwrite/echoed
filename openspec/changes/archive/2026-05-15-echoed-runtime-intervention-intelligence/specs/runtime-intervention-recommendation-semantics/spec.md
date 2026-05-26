## ADDED Requirements

### Requirement: Educator runtime intervention recommendations are bounded and deterministic
The system SHALL derive educator-facing runtime intervention recommendations from existing governed evidence using a bounded, deterministic recommendation taxonomy of `reteach`, `review`, `enrichment`, `monitor`, and `normal`.

#### Scenario: Reteach recommendation is derived from recent governed evidence
- **WHEN** existing governed assessment or mastery evidence indicates a learner needs direct concept re-teaching within the current learning path
- **THEN** the system SHALL return a `reteach` recommendation for authorized educator visibility

#### Scenario: Review recommendation is derived from bounded recovery evidence
- **WHEN** existing governed evidence indicates a learner should revisit recent material or reinforcement context without full concept re-teaching
- **THEN** the system SHALL return a `review` recommendation for authorized educator visibility

#### Scenario: Enrichment recommendation is derived from strong safe evidence
- **WHEN** existing governed evidence indicates strong recent mastery or support for optional extension
- **THEN** the system SHALL return an `enrichment` recommendation for authorized educator visibility

#### Scenario: Monitor recommendation is derived from cautionary but non-blocking evidence
- **WHEN** existing governed evidence suggests educator attention is useful but does not justify reteach, review, or enrichment as the primary recommendation
- **THEN** the system SHALL return a `monitor` recommendation for authorized educator visibility

#### Scenario: Normal continuation recommendation is derived when no intervention state applies
- **WHEN** existing governed evidence does not justify reteach, review, enrichment, or monitor
- **THEN** the system SHALL return a `normal` continuation recommendation for authorized educator visibility

### Requirement: Every recommendation includes explainable evidence basis
The system SHALL attach an evidence basis to each runtime intervention recommendation so educators can understand which governed evidence sources contributed to the recommendation.

#### Scenario: Recommendation includes bounded evidence basis
- **WHEN** a runtime intervention recommendation is returned
- **THEN** the system SHALL include bounded evidence-basis details that identify the relevant governed evidence, support context, or mastery interpretation used

#### Scenario: Recommendation evidence basis remains deterministic
- **WHEN** the same governed evidence is evaluated repeatedly without state mutation
- **THEN** the system SHALL return the same recommendation state and evidence basis each time

### Requirement: Recommendation confidence and caution framing is non-predictive
The system SHALL express recommendation certainty through bounded confidence or caution framing that reflects evidence quality and integrity constraints rather than learner ability or predicted behavior.

#### Scenario: Recommendation indicates confidence when safe evidence is sufficient
- **WHEN** the recommendation is derived from valid, explainable, and historically safe evidence
- **THEN** the system SHALL allow a confident recommendation framing

#### Scenario: Recommendation indicates caution when evidence quality is limited
- **WHEN** the recommendation is derived from sparse, ambiguous, or partially limited evidence that remains usable for educator awareness
- **THEN** the system SHALL attach caution framing without predicting learner outcomes or ability

### Requirement: Recommendation tone remains learner-safe and educator-bounded
The system SHALL keep runtime intervention recommendation semantics confidence-preserving, non-shaming, non-deficit-based, and bounded to educator judgment support.

#### Scenario: Recommendation wording avoids learner labeling
- **WHEN** educator-facing runtime intervention recommendation content is presented
- **THEN** the system SHALL avoid shaming, deficit framing, manipulative gamification, and ability or behavior prediction

#### Scenario: Recommendation does not replace educator judgment
- **WHEN** runtime intervention recommendations are shown to educators
- **THEN** the system SHALL present them as bounded guidance rather than automatic intervention directives
