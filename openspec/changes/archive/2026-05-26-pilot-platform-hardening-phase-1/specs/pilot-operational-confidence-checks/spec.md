## ADDED Requirements

### Requirement: Bounded pilot operational confidence checks

The system SHALL provide a bounded readiness verification layer for pilot-critical EchoEd flows without expanding into a full end-to-end platform test suite.

#### Scenario: Operator validates pilot readiness
- **WHEN** a pilot operator runs the documented validation flow
- **THEN** the flow confirms the student login, active-course discovery, lesson entry, and safe return expectations
- **AND** it confirms the teacher can reach a stable dashboard state with enough course and learner visibility for a pilot walkthrough

### Requirement: Pilot confidence checks remain aligned with existing regression authorities

The system SHALL treat backend pytest, frontend Angular tests, and the existing student browser smoke as the authoritative automated confidence layers for Phase 1.

#### Scenario: Phase 1 validation is reviewed
- **WHEN** the pilot hardening verification strategy is inspected
- **THEN** it includes the existing backend test suite, existing Angular tests, and the bounded student smoke path
- **AND** it does not depend on weakened auth, mocked runtime shortcuts, or undocumented manual database repair

### Requirement: Confidence documentation states its boundaries

The system SHALL document what the pilot-confidence flow proves and what remains intentionally manual or out of scope.

#### Scenario: Operator reads the validation runbook
- **WHEN** a pilot operator prepares EchoEd for a walkthrough
- **THEN** the documentation explains which checks are automated, which teacher validations remain manual, and which broader resilience concerns are not covered by Phase 1
