## ADDED Requirements

### Requirement: Authoring APIs persist the complete canonical course graph consistently
The platform SHALL provide authorized authoring contracts that create, retrieve, and transactionally update canonical course metadata, units, lessons, activities, sources, and assessment references within organization scope while preserving learner-facing API behavior.

#### Scenario: Authorized creator creates a durable draft
- **WHEN** an authorized creator submits valid minimum course identity with an idempotency key
- **THEN** the authoring API creates one organization-scoped draft, returns its identifier and revision, and returns the same result for a safe retry of the same creation request

#### Scenario: Authorized creator saves a nested course graph
- **WHEN** an authorized creator submits a valid course graph update against the current revision
- **THEN** the API persists the nested change transactionally, maintains deterministic ordering, and returns the next revision

#### Scenario: Nested graph persistence fails
- **WHEN** any required part of a course-graph mutation fails validation or persistence
- **THEN** the API returns structured issue context and does not commit a partial graph update

#### Scenario: Learner reads the updated course
- **WHEN** a learner requests the course after an authoring update
- **THEN** the existing audience-aware and publication-aware learner contract remains authoritative and excludes non-deliverable content

### Requirement: Authoring APIs protect concurrent revisions
The platform SHALL require a current revision token for updates to durable course drafts and SHALL return an explicit conflict response for stale writes.

#### Scenario: Creator saves a stale revision
- **WHEN** an authoring update references a revision older than the current server revision
- **THEN** the API rejects the update without overwriting newer work and returns enough bounded metadata for the client to reload or recover

### Requirement: Legacy authoring routes converge on the canonical authoring service
During migration, any retained legacy course creation or update route SHALL enforce equivalent authorization, validation, transactional persistence, and ordering through the canonical authoring domain service.

#### Scenario: Legacy client creates or edits a course during migration
- **WHEN** a supported legacy client invokes a retained course write route
- **THEN** the route delegates to the canonical authoring service and cannot bypass organization scope, idempotency, validation, or governance invariants

