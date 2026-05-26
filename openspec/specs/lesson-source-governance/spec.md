# lesson-source-governance Specification

## Purpose
TBD - created by archiving change echoed-content-review-governance. Update Purpose after archive.
## Requirements
### Requirement: Governed lessons require at least one cited source
The system SHALL require lessons entering `reviewed` or `approved` states to include at least one linked source with a non-empty citation.

#### Scenario: Reviewer submits a lesson with no sources
- **WHEN** a lesson is transitioned toward `reviewed` or `approved` without any linked sources
- **THEN** the system rejects the transition as not ready

#### Scenario: Reviewer submits a lesson with an empty citation
- **WHEN** a lesson includes a source record without a citation during readiness evaluation
- **THEN** the system treats the lesson as not ready for governed publication

### Requirement: Source URLs are validated during governance checks
The system SHALL validate any provided source URL before a lesson can pass readiness for reviewed or approved publication states.

#### Scenario: Source URL is syntactically invalid
- **WHEN** a source record includes a malformed URL and the lesson is evaluated for governance readiness
- **THEN** the system rejects readiness with a source validation error

#### Scenario: Source omits a URL but includes a citation
- **WHEN** a source record includes a citation and no URL
- **THEN** the system still treats the source as valid for readiness

