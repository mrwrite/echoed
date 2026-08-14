# Platform Audit Events Specification

## Purpose

Define EchoEd's durable, privacy-minimized, transaction-bound audit-event contract for approved high-impact actions, scoped administrative review, integrity verification, retention, export, and operational recovery.

## Requirements

### Requirement: Durable audit-event schema
The system MUST persist approved high-impact events using an explicit versioned schema containing event ID, timestamp, actor identity and role snapshot, action, category, outcome, target type and identifier, optional organization scope, request and correlation identifiers, minimized before/after state, safe reason code, and integrity metadata. The schema MUST NOT store credentials, tokens, authorization headers, cookies, private content, assessment answers, uploaded bytes, filenames, or unnecessary personal data.

#### Scenario: High-impact action captured
- **WHEN** an approved administrative mutation succeeds
- **THEN** exactly one durable event records the allowlisted attribution and state-transition fields without protected content

#### Scenario: Unsafe audit payload rejected
- **WHEN** code attempts to persist a sensitive key or unsupported nested value
- **THEN** audit persistence fails closed without writing the unsafe event or committing the associated mutation

### Requirement: Atomic mutation and event persistence
The system MUST write successful high-impact mutation events in the same database transaction as their business-state changes. A mutation MUST roll back when its required audit event cannot be persisted, and a rolled-back mutation MUST NOT leave a success event.

#### Scenario: Audit persistence failure
- **WHEN** required audit-event persistence fails during a role change
- **THEN** neither the role change nor a success audit event is committed

#### Scenario: Business mutation rollback
- **WHEN** a high-impact mutation is rolled back after an audit row is staged
- **THEN** the audit row is rolled back in the same transaction

### Requirement: Approved action coverage
The system SHALL maintain an explicit action catalog and MUST capture currently supported platform-role changes, account deletion, organization invitation and membership changes, forum moderation, and Course Studio publish/review/restore transitions. Unsupported actions MUST NOT be fabricated as successful audit events.

#### Scenario: Covered mutation catalog
- **WHEN** a supported covered mutation succeeds
- **THEN** its stable catalog action is present in the durable audit store

#### Scenario: Denied mutation
- **WHEN** authorization or safety controls deny a requested mutation
- **THEN** no successful durable mutation event is recorded and existing operational security diagnostics remain available

### Requirement: Append-only and integrity verification
Application APIs MUST NOT update or delete audit events. Each event MUST include canonical integrity-chain metadata scoped to platform or organization, and repository tooling MUST verify ordering and content integrity. The documentation MUST state that this is tamper-evident application data rather than protection from a fully privileged database operator.

#### Scenario: API mutation attempt
- **WHEN** a client attempts to update or delete an audit event
- **THEN** no supported route permits the operation

#### Scenario: Integrity verification
- **WHEN** an operator verifies an unchanged audit chain
- **THEN** verification succeeds, while modified or reordered canonical event data causes verification to fail

### Requirement: Scoped audit review
The backend MUST enforce explicit audit-read allowlists. Platform administrators SHALL read the minimized platform feed, and active organization administrators SHALL read only events scoped to their organization. Cross-organization IDs MUST NOT bypass scope checks or disclose event contents.

#### Scenario: Platform audit review
- **WHEN** an authorized platform administrator requests the platform audit feed
- **THEN** a bounded minimized result is returned

#### Scenario: Organization audit review
- **WHEN** an active organization administrator requests their organization audit feed
- **THEN** only events whose organization scope matches the active membership are returned

#### Scenario: Cross-organization audit request
- **WHEN** an organization administrator supplies another organization's identifier
- **THEN** access is denied or concealed according to the security error policy without returning event metadata

### Requirement: Bounded filtering and pagination
Audit reads MUST use stable bounded pagination and allowlisted low-cardinality filters for time, action, category, outcome, actor ID, and target type/ID. Invalid filters and limits MUST fail validation, and responses MUST NOT serialize ORM models directly.

#### Scenario: Filtered page
- **WHEN** an authorized reviewer supplies valid filters and a bounded page cursor
- **THEN** the API returns only matching explicit response records plus a continuation cursor

#### Scenario: Excessive page size
- **WHEN** a client requests more than the configured maximum page size
- **THEN** request validation rejects or caps the request according to the documented API contract

### Requirement: Safe audit export
Authorized reviewers SHALL export only the same scoped, filtered, minimized fields available through review APIs. Export size MUST be capped, spreadsheet-formula injection MUST be neutralized, and each successful export MUST itself create a durable audit event.

#### Scenario: Authorized CSV export
- **WHEN** an authorized platform administrator exports a bounded filtered audit set
- **THEN** the response is a safe CSV attachment and an `audit.exported` event records the operation without embedding exported contents

#### Scenario: Unauthorized export
- **WHEN** an actor without audit-read permission requests an export
- **THEN** the request fails without disclosing whether matching events exist

### Requirement: Retention and preservation controls
The system SHALL document retention ownership and provide dry-run-first operator tooling for bounded expiration. Production deletion MUST require explicit environment acknowledgement, a verified backup reference, and confirmation that no preservation hold applies. Retention MUST NOT be exposed as a public API.

#### Scenario: Retention dry run
- **WHEN** an operator supplies a cutoff without destructive confirmation
- **THEN** tooling reports only aggregate eligible counts and changes no data

#### Scenario: Preservation hold
- **WHEN** a preservation hold is active for the requested scope or period
- **THEN** retention deletion fails closed

### Requirement: Accessible administrative review
The Angular application SHALL provide authorized platform administrators an accessible audit review experience with loading, empty, error, filtered, detail, pagination, and export states. Frontend controls MUST mirror but MUST NOT replace backend authorization.

#### Scenario: Administrator reviews an event
- **WHEN** an authorized administrator opens the audit review route and selects an event
- **THEN** minimized attribution, action, outcome, scope, timestamp, and safe state changes are presented with accessible labels

#### Scenario: Audit API failure
- **WHEN** audit loading or export fails
- **THEN** the page presents an accessible safe error with request-reference context where available and does not retain stale protected results

### Requirement: Audit-store observability and privacy
Audit capture, read, export, verification, and retention operations MUST emit privacy-safe operational metrics/logs without duplicating before/after contents or using actor, target, organization, or event IDs as metric labels. Durable audit events and operational diagnostics MUST remain conceptually distinct.

#### Scenario: Audit persistence failure signal
- **WHEN** required audit persistence fails
- **THEN** a bounded operational failure signal includes request correlation and category but excludes the attempted state payload
