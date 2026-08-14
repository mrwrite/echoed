# Platform Operational Readiness Specification

## Purpose

Define EchoEd's evidence-backed contract for safe production configuration, deployment, migration, health checking, shutdown, monitoring, backup, restore, rollback, and operational recovery without expanding into hosting infrastructure or durable audit events.

## Requirements

### Requirement: Fail-closed production configuration
The system MUST validate security-sensitive and operational configuration before serving production traffic, MUST reject missing, malformed, contradictory, unsafe, or development-only values, and MUST report actionable setting categories without exposing secret values. Development and test environments SHALL retain usable local configuration.

#### Scenario: Valid production configuration
- **WHEN** an operator supplies every required production setting with mutually consistent safe values
- **THEN** validation succeeds before application initialization and exposes no setting values

#### Scenario: Unsafe production configuration
- **WHEN** a production setting is absent, malformed, uses a known development default, or contradicts another setting
- **THEN** startup fails before traffic is served and identifies only the affected setting or category

### Requirement: Trusted host and proxy boundary
The backend MUST enforce an explicit host allowlist and MUST treat forwarding metadata as authoritative only when proxy trust is enabled and the direct peer is in an explicit IP or CIDR allowlist. Untrusted forwarding metadata MUST NOT alter the authoritative client address, protocol, or host.

#### Scenario: Allowed and rejected hosts
- **WHEN** requests use an allowed host and then a host outside the configured allowlist
- **THEN** the allowed request is processed and the unexpected host is rejected

#### Scenario: Spoofed forwarding metadata
- **WHEN** an untrusted direct client supplies forwarding headers
- **THEN** the backend uses direct connection metadata rather than the supplied forwarding values

#### Scenario: Trusted forwarding metadata
- **WHEN** a configured trusted proxy supplies valid bounded forwarding headers
- **THEN** the backend resolves the forwarded client, protocol, and host according to the documented topology

### Requirement: Deterministic deployment and migration lifecycle
The repository SHALL provide deterministic pre-deployment validation, explicit database migration, application startup, liveness/readiness, smoke, monitoring, and rollback decision procedures. Normal production application startup MUST NOT automatically execute migrations.

#### Scenario: Successful release lifecycle
- **WHEN** an operator validates configuration, executes required migrations, starts the immutable release, and runs post-deployment checks
- **THEN** each gate produces a clear pass/fail result before the release proceeds

#### Scenario: Migration failure
- **WHEN** a migration fails or the database schema does not reach the repository heads
- **THEN** application rollout is stopped and no automatic downgrade is claimed

### Requirement: Explicit rollback boundaries
Operational documentation MUST distinguish application, configuration, and database rollback and MUST identify schema compatibility conditions under which application-only rollback is unsafe.

#### Scenario: Compatible application rollback
- **WHEN** a failed release has no incompatible schema or configuration transition
- **THEN** the operator can redeploy the previous immutable artifact and verify readiness and smoke checks

#### Scenario: Incompatible schema transition
- **WHEN** the previous application cannot operate safely against the migrated schema
- **THEN** the procedure requires a verified downgrade or backup restore rather than application-only rollback

### Requirement: Operational health and graceful shutdown
The lifecycle MUST use process-only liveness, dependency-aware readiness, and bounded graceful shutdown. Database unavailability MUST fail readiness without failing liveness, health output MUST remain non-disclosing, and shutdown MUST release application/database resources and emit bounded operational events.

#### Scenario: Database unavailable
- **WHEN** the database dependency is unavailable
- **THEN** liveness remains healthy while readiness returns an unavailable status without connection details

#### Scenario: Graceful termination
- **WHEN** the server receives a controlled termination request
- **THEN** it stops accepting work according to server semantics, allows bounded in-flight completion, executes shutdown hooks, and releases database resources

### Requirement: Service objectives and alert ownership
The system documentation SHALL define measurable initial availability, successful-request, error-rate, latency, and readiness indicators with targets, windows, known limitations, alert conditions, severity, response, owner role, escalation path, and runbook. It MUST distinguish exposed signals from external aggregation and notification infrastructure that is not configured.

#### Scenario: Operator evaluates a service objective
- **WHEN** an operator reviews the documented Phase 10 health, metric, and log signals
- **THEN** the indicator formula, target, window, data limitations, owner, and related response are unambiguous

### Requirement: Persistent-state backup and verified restore
The operational contract MUST identify all persistent state and define backup scope, cadence, retention, encryption, separation, integrity verification, and restore testing. A backup SHALL NOT be considered valid until an isolated restore proves database and supported uploaded-asset usability.

#### Scenario: Safe recovery drill
- **WHEN** an operator backs up disposable database and upload data, verifies the manifest, restores to isolated targets, and runs usability checks
- **THEN** the restored records and asset bytes match the originals without exposing sensitive data

#### Scenario: Corrupted backup
- **WHEN** a backup file no longer matches its integrity manifest
- **THEN** restore fails closed before replacing the target state

### Requirement: Storage ownership and recovery targets
Documentation MUST identify the source of truth, persistence boundary, backup owner, restore owner, deployment behavior, and loss consequences for database, uploaded assets, generated static assets, configuration, and secrets. It SHALL define defensible initial RPO and RTO targets and their prerequisites and limitations.

#### Scenario: Ephemeral storage configuration
- **WHEN** production upload paths do not have an explicit persistent-storage decision
- **THEN** production configuration validation fails rather than silently accepting ephemeral ownership

### Requirement: Secret rotation and environment separation
Production MUST NOT silently load development secrets or insecure defaults. The operational contract SHALL define preparation, sequencing, verification, invalidation where supported, and emergency rollback for rotating application secrets and credentials while keeping secret values out of repository artifacts and evidence.

#### Scenario: Rotation simulation
- **WHEN** an operator validates old and replacement production configurations in an isolated simulation
- **THEN** both configurations pass only with independently supplied safe secrets and no secret value appears in output

### Requirement: Evidence-driven operational drills
The repository SHALL provide repeatable safe drills for invalid production configuration, unavailable database/readiness, startup, shutdown, health, failed post-deploy verification, backup, restore, rollback, configuration rotation, and storage recovery. Each drill MUST define prerequisites, procedure, expected and observed behavior, and pass/fail criteria and MUST refuse production or uncontrolled data where automation could be destructive.

#### Scenario: Complete local drill execution
- **WHEN** an engineer runs the operational drill suite against isolated test resources
- **THEN** every supported drill records a deterministic pass/fail result and temporary resources are removed

### Requirement: Security and observability preservation
Operational readiness MUST preserve Phase 8 authorization and privacy controls and Phase 10 logging, correlation, metrics, and health behavior. Logs, metrics, health output, errors, documentation, and drill evidence MUST NOT expose credentials, tokens, authorization data, private content, uploaded bytes, SQL values, or private user information.

#### Scenario: Operational failure evidence
- **WHEN** validation, readiness, backup integrity, or deployment verification fails
- **THEN** diagnostics identify the operational category and safe reference context without exposing protected values

### Requirement: Explicit deferred capability boundary
The change MUST NOT implement durable platform audit events, distributed rate limiting/state, identity redesign, new hosting infrastructure, distributed observability expansion, or application feature work.

#### Scenario: Future audit-event need
- **WHEN** an operational workflow needs durable tamper-resistant administrative history
- **THEN** the need is recorded for `implement-platform-audit-events` rather than implemented in this capability
