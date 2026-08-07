## ADDED Requirements

### Requirement: Authentication and authorization outcomes produce bounded operational signals
The platform SHALL record privacy-safe operational events and low-cardinality metrics for authentication success/failure, authorization denial, cross-organization denial, and rate-limit triggers without changing backend authority decisions or exposing account identifiers, tokens, organization names, or protected target data as metric labels.

#### Scenario: Login succeeds
- **WHEN** valid credentials produce a session token
- **THEN** the backend records an authentication success outcome correlated to the request without logging the credentials or token

#### Scenario: Organization-scoped authorization is denied
- **WHEN** an authenticated actor fails an organization role or membership policy
- **THEN** the backend records a bounded authorization denial category while preserving the existing 403 or concealment behavior

#### Scenario: Authentication is throttled
- **WHEN** the configured authentication limiter returns 429
- **THEN** the security event and operational rate-limit metric share request correlation without exposing the account identifier or limiter storage key
