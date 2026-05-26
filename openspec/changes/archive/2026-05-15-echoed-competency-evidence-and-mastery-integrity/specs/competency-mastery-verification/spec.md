## ADDED Requirements

### Requirement: Competency-evidence integrity changes SHALL be regression-verifiable
The implementation SHALL include focused regression coverage for evidence traceability, deprecated or superseded assessment safety, incompatible revision warnings, runtime support guardrails, staff visibility, and certification/reporting preservation.

#### Scenario: Evidence traceability and compatibility behavior are implemented
- **WHEN** competency-evidence integrity logic is added or changed
- **THEN** focused tests SHALL verify traceable mastery evidence, compatibility classification, and historical evidence preservation
- **AND** the tests SHALL prove that old attempts are not reassigned to new assessment revisions

#### Scenario: Runtime support and staff visibility are updated
- **WHEN** runtime support or staff/admin surfaces consume competency-integrity results
- **THEN** tests SHALL verify read-only behavior, learner non-exposure, and deterministic fallback behavior for unsafe evidence

### Requirement: Competency-evidence integrity SHALL not regress governed platform semantics
The implementation SHALL verify that assessment scoring, certification behavior, reporting behavior, and governed progression semantics remain unchanged unless an explicit compatibility-safe rule adds bounded interpretation context.

#### Scenario: Integrity rules are introduced alongside existing reporting and runtime support
- **WHEN** the system adds competency-evidence and mastery-integrity rules
- **THEN** focused regression coverage SHALL verify no unintended mutation or semantic rewrite of progression, scoring, certification, or reporting behavior
- **AND** governed learner delivery SHALL remain intact
