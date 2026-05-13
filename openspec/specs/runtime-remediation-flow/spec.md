# runtime-remediation-flow Specification

## Purpose
TBD - created by archiving change echoed-runtime-remediation-and-reinforcement. Update Purpose after archive.
## Requirements
### Requirement: Bounded runtime remediation continuation
The platform SHALL define bounded runtime remediation continuation that reuses governed delivery, assessment evidence, mastery summaries, and current learner state without introducing a second progression engine.

#### Scenario: Weak mastery triggers support without replacing progression
- **WHEN** a learner produces a weak mastery signal within the existing assessment and mastery foundation
- **THEN** the platform MUST be able to express a remediation-aware continuation state
- **AND** governed progression MUST remain the canonical authority for lesson sequencing and availability

### Requirement: Supportive recovery and retry semantics
The platform SHALL define supportive retry, review, and re-engagement semantics for remediation flows that preserve learner dignity and momentum.

#### Scenario: Recovery flow remains emotionally safe
- **WHEN** a learner enters a remediation-aware runtime state
- **THEN** the recovery flow MUST use bounded retry/review semantics
- **AND** it MUST NOT introduce punitive failure loops or shame-based learner messaging

