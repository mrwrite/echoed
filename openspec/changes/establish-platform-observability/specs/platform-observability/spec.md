## ADDED Requirements

### Requirement: Backend diagnostics are structured and privacy-conscious
The backend SHALL emit environment-configurable events with stable names, severity, component, environment, request/correlation context, and allowlisted operational fields while centrally redacting secrets and excluding request bodies, protected content, and unnecessary personal data.

#### Scenario: JSON logging is enabled
- **WHEN** the configured log format is JSON
- **THEN** each application event is serialized as a structured object with stable field names and no secret values

#### Scenario: Nested sensitive data reaches the logger
- **WHEN** an event contains authorization, cookie, password, token, or secret fields in nested data
- **THEN** the sensitive values are replaced before formatting and never appear in emitted output

### Requirement: Requests have safe identity and correlation context
The backend SHALL establish a canonical safe request ID for every request by accepting only a strictly bounded safe upstream value or generating a new identifier, return it in `X-Request-ID`, make it available to logs/error handlers, and treat a sanitized caller correlation hint separately from request and distributed trace identity.

#### Scenario: Request has no correlation headers
- **WHEN** a request enters the API without an accepted correlation hint
- **THEN** the server replaces it with a generated request ID and returns it without trusting caller identity

#### Scenario: Caller supplies invalid correlation text
- **WHEN** `X-Correlation-ID` exceeds the limit or contains disallowed characters
- **THEN** the server discards it and does not include it in logs or responses

### Requirement: HTTP and exception instrumentation is safe and low-cardinality
The platform SHALL observe request count, active requests, normalized route, status family, and duration without recording raw queries, bodies, personal identifiers, or raw object IDs as metric labels, and SHALL categorize validation, authorization, dependency, and unexpected failures safely.

#### Scenario: Parameterized route completes
- **WHEN** a request to a route containing a resource identifier completes
- **THEN** logs and metrics use the normalized route template rather than the supplied identifier

#### Scenario: Unexpected exception occurs
- **WHEN** application code raises an unhandled exception
- **THEN** the server logs one categorized exception with request context and returns a generic 500 response containing only a safe reference ID

### Requirement: Liveness and readiness have distinct non-disclosing behavior
The platform SHALL expose process-only liveness and bounded mandatory-dependency readiness using machine-readable responses that omit credentials, host internals, versions, database names, and exception details.

#### Scenario: Database is unavailable
- **WHEN** the process is running but the database readiness probe fails
- **THEN** liveness remains successful, readiness returns 503, and a safe database failure signal is emitted

### Requirement: Vendor-neutral operational metrics are protected
The platform SHALL collect documented low-cardinality operational metrics without a commercial vendor and SHALL conceal metrics export unless explicitly enabled and authenticated by deployment configuration.

#### Scenario: Metrics endpoint is disabled
- **WHEN** a client requests the metrics route under default configuration
- **THEN** the route returns 404 and exposes no metric names or application state

#### Scenario: Authorized operator reads metrics
- **WHEN** metrics collection/export is enabled and the caller supplies the configured access token
- **THEN** the backend returns a standard Prometheus text representation without personal-data labels

### Requirement: Database failures are observable without SQL data leakage
Database connection, readiness, rollback, and operation failures SHALL emit stable events and bounded metrics without unrestricted SQL echo, bound values, credentials, or protected record data.

#### Scenario: Transaction fails
- **WHEN** a database-backed operation raises a SQLAlchemy failure
- **THEN** the transaction is rolled back and a safe database operation failure is correlated to the request

### Requirement: Course Studio critical operations are observable
The platform SHALL emit high-level log and metric outcomes for supported Course Studio import, draft create/save/conflict, preview, review, publish, restore, and template operations without logging course graphs, lesson content, assessment answers, feedback text, or imported documents.

#### Scenario: Draft save conflicts
- **WHEN** an author submits a stale revision and the backend rejects it
- **THEN** the platform records a bounded draft-save conflict outcome correlated to the request while preserving existing conflict behavior

#### Scenario: Publish fails safety validation
- **WHEN** a publish attempt is blocked by safe-publish validation
- **THEN** the platform records publish attempt/failure signals without serializing validation content or course material

### Requirement: Frontend errors retain safe backend references
Angular SHALL extract safe request references from backend responses, preserve accessible user-facing error behavior and entered work, and avoid sending or logging tokens, protected content, raw error bodies, or stack traces to any external vendor.

#### Scenario: Unexpected API failure has request header
- **WHEN** Angular receives an unexpected server error with `X-Request-ID`
- **THEN** the user may receive a copyable safe reference while routine validation messages remain uncluttered

#### Scenario: Course autosave fails
- **WHEN** an autosave request fails
- **THEN** unsaved authoring state remains available and diagnostics retain only operation, status, and safe request reference

### Requirement: Actual background work has explicit observability boundaries
The platform SHALL document whether workers or scheduled tasks exist and SHALL require future real background execution to record start, success, failure, duration, retry, terminal failure, and safe correlation without inventing a queue in this change.

#### Scenario: No executable worker exists
- **WHEN** repository background-work paths are audited
- **THEN** metadata-only job records are not represented as an operational queue or assigned fabricated queue-depth metrics

### Requirement: Observability overhead and operations are documented
The change SHALL measure representative local instrumentation overhead, provide vendor-neutral health/log/metric/runbook guidance, and preserve a concrete boundary for durable audit events without claiming production-scale performance or readiness.

#### Scenario: Operator investigates a frontend reference
- **WHEN** support receives a safe request reference
- **THEN** the runbook explains how to correlate it with backend logs without requesting credentials, tokens, learner content, or uploaded files

#### Scenario: Durable audit history is requested
- **WHEN** an operator needs append-only retained actor/action/target history
- **THEN** documentation directs that requirement to `implement-platform-audit-events` rather than treating operational logs as authoritative history
