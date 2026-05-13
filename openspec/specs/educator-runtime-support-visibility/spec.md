# educator-runtime-support-visibility Specification

## Purpose
TBD - created by archiving change echoed-educator-runtime-visibility. Update Purpose after archive.
## Requirements
### Requirement: Educators can see learner runtime support state
The system SHALL expose a read-only runtime support state for educators that identifies whether a flagship learner is continuing normally, needs remediation support, or is ready for enrichment.

#### Scenario: Educator sees remediation support state
- **WHEN** a flagship learner has weak recent assessment or mastery evidence that maps to remediation guidance
- **THEN** educator-facing visibility SHALL identify the learner as needing remediation support

#### Scenario: Educator sees enrichment support state
- **WHEN** a flagship learner has strong recent assessment and mastery evidence that maps to enrichment guidance
- **THEN** educator-facing visibility SHALL identify the learner as ready for enrichment support

#### Scenario: Educator sees normal continuation state
- **WHEN** a flagship learner has no special runtime support condition beyond governed continuation
- **THEN** educator-facing visibility SHALL identify the learner as continuing normally

