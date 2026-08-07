## 1. Preconditions and architecture evidence

- [x] 1.1 Confirm Phase 8 strict completion/archive state, other requested change states, branch/commit, dirty-tree boundaries, test baselines, and preserve unrelated work
- [x] 1.2 Complete the current observability audit across backend, Angular, dependencies, CI, deployment health, Course Studio, database, security events, and actual background-work architecture
- [x] 1.3 Define canonical logging, correlation, metrics, health, database, frontend, redaction, Course Studio, and durable-audit boundary documentation

## 2. Structured logging and request lifecycle

- [x] 2.1 Add environment-validated observability settings with JSON/developer formatting, log level, request logging, metrics/export, correlation header, and slow-request controls
- [x] 2.2 Implement centralized recursive sensitive-data redaction and structured event emission with stable names/context
- [x] 2.3 Replace request middleware with canonical bounded-or-generated request IDs, separate sanitized correlation hints, context propagation/reset, response headers, normalized routes, and security headers
- [x] 2.4 Add safe HTTP lifecycle/slow request metrics and structured completion events using bounded labels
- [x] 2.5 Add categorized validation, HTTP denial, database/dependency, and unexpected-exception handling with generic request-reference responses

## 3. Health, metrics, and database

- [x] 3.1 Implement a locked vendor-neutral counter/gauge/histogram registry with documented allowlisted label dimensions
- [x] 3.2 Add disabled-by-default, token-protected Prometheus text export with concealment and constant-time token comparison
- [x] 3.3 Preserve process-only liveness and implement bounded, non-disclosing database readiness success/failure signals
- [x] 3.4 Instrument database session failures/rollbacks and readiness connection failures without SQL text or bound values
- [x] 3.5 Add backend tests for settings validation, metrics presence/security/cardinality, liveness/readiness failure, database failure events, and safe health responses

## 4. Domain and security observability

- [x] 4.1 Integrate Phase 8 security events into structured logs and bounded security metrics without creating durable audit persistence
- [x] 4.2 Instrument authentication registration/login success/failure/throttle outcomes without account-existence or credential disclosure
- [x] 4.3 Instrument platform/organization authorization denials and cross-organization categories without protected target data
- [x] 4.4 Instrument upload attempt/success/rejection/duration and limiter outcomes without filenames, bytes, or personal labels
- [x] 4.5 Instrument Course Studio import, draft create/save/conflict, preview, review, publish, restore/duplicate/template outcomes at supported API boundaries
- [x] 4.6 Add backend regression tests for security/auth/authz/rate-limit/upload/Course Studio events and secret-free structured output

## 5. Frontend diagnostic alignment

- [x] 5.1 Add a privacy-safe Angular diagnostic service for request-reference extraction, unexpected-error references, operation/status categories, and sanitized console behavior
- [x] 5.2 Add an Angular HTTP diagnostic interceptor and global error handler without duplicating user-facing security handling or logging raw errors/content
- [x] 5.3 Integrate safe references into unexpected API, lazy-chunk, upload, authentication-expiry, and permission/rate-limit behavior where appropriate
- [x] 5.4 Add Course Studio autosave/publish failure diagnostics that preserve work and exclude graphs, lesson content, imports, tokens, and raw bodies
- [x] 5.5 Add Angular tests for reference extraction/display, global/lazy diagnostics, autosave/publish failures, and sensitive-data exclusion
- [x] 5.6 Add only stable user-visible Playwright coverage for safe server references and preserved role/error workflows

## 6. Operations, performance, and verification

- [x] 6.1 Create the observability runbook and incident guide covering required detection, correlation, containment, escalation, and safe evidence handling
- [x] 6.2 Update architecture, security, README, roadmap, Phase 8 security-event, platform observability baseline, and future audit-event dependency documentation
- [x] 6.3 Measure local instrumentation overhead for representative health/auth/Course Studio operations and document method, results, and non-production limitations
- [x] 6.4 Run complete backend tests and repository-supported backend syntax/dependency/format/lint checks without baseline regression
- [x] 6.5 Run complete Angular tests, production build, repository-supported frontend format/lint checks, and production dependency audit without baseline regression
- [x] 6.6 Run complete Playwright tests, strict OpenSpec validation, `git diff --check`, secret/temp-artifact checks, remove disposable services/data/logs, and publish Phase 10 verification evidence
