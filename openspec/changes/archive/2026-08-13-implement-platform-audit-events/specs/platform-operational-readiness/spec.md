## MODIFIED Requirements

### Requirement: Persistent-state backup and verified restore
The operational contract MUST identify all persistent state, including durable audit events and their integrity metadata, and define backup scope, cadence, retention, encryption, separation, integrity verification, and restore testing. A backup SHALL NOT be considered valid until an isolated restore proves database, audit-chain, and supported uploaded-asset usability. Audit retention MUST NOT remove the only recoverable copy required by incident or preservation policy.

#### Scenario: Safe recovery drill
- **WHEN** an operator backs up disposable database and upload data, verifies the manifest, restores to isolated targets, verifies the restored audit chain, and runs usability checks
- **THEN** the restored records, audit integrity metadata, and asset bytes match the originals without exposing sensitive data

#### Scenario: Corrupted backup
- **WHEN** a backup file no longer matches its integrity manifest
- **THEN** restore fails closed before replacing the target state

#### Scenario: Audit-event recovery
- **WHEN** an operator restores a database containing durable audit events
- **THEN** audit-chain verification succeeds before the restored service is accepted for operational use
