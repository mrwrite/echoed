# adaptive-continuation-semantics Specification

## Purpose
TBD - created by archiving change echoed-runtime-remediation-and-reinforcement. Update Purpose after archive.
## Requirements
### Requirement: Runtime “what’s next” guidance
The platform SHALL define runtime continuation guidance that can reflect remediation-aware and enrichment-aware learner state while preserving deterministic governed progression.

#### Scenario: Continuation remains governed and explainable
- **WHEN** the learner asks or is shown what comes next
- **THEN** the platform MUST be able to distinguish between canonical governed continuation and bounded runtime support guidance
- **AND** the support guidance MUST remain explainable from current evidence and learner state

### Requirement: Learner pacing continuity
The platform SHALL define pacing continuity semantics for runtime support so learners can recover or extend without losing orientation or session coherence.

#### Scenario: Support state does not break continuity
- **WHEN** a learner transitions into remediation or enrichment support
- **THEN** the platform MUST preserve continuity across session bootstrap, learner progress context, and next-step guidance
- **AND** it MUST NOT create ambiguous or conflicting continuation paths

