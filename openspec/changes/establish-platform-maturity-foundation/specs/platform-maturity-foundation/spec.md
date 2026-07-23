## ADDED Requirements

### Requirement: Measured frontend bundle optimization
The system SHALL generate evidence-based Angular production bundle measurements before and after optimization, and the optimized initial bundle SHALL remain at or below the configured 1.25 MB warning budget without increasing that budget to hide the warning.

#### Scenario: Production bundle meets the existing budget
- **WHEN** the optimized frontend production build completes
- **THEN** the build reports an initial bundle no larger than 1.25 MB and does not emit the original initial-bundle warning

#### Scenario: Optimization evidence is reviewable
- **WHEN** an optimization is documented
- **THEN** its previous behavior, new behavior, measured size effect, user effect, risk, coverage, and rollback consideration are recorded

### Requirement: Compatible route loading architecture
The system SHALL load independently navigable feature areas lazily where justified while preserving direct navigation, guards, accessible loading behavior, browser history, mobile navigation, legacy route behavior, and role functionality.

#### Scenario: Protected deep route is refreshed
- **WHEN** an authorized user directly opens or refreshes a protected feature route
- **THEN** the feature loads successfully through its configured lazy boundary without bypassing its route guards

#### Scenario: Unauthorized feature route is requested
- **WHEN** a role without permission requests a protected feature route
- **THEN** access remains denied and protected functionality is not made available

#### Scenario: Lazy chunk cannot load
- **WHEN** an optional route chunk fails to load
- **THEN** the application provides recoverable error behavior rather than an inaccessible or permanently blank state

### Requirement: Reproducible runtime performance baseline
The project SHALL document reproducible runtime observations for representative public, authentication, learner, teacher, Studio, Organization, and Platform Admin routes and SHALL distinguish collected measurements from blocked metrics and code-inspection inferences.

#### Scenario: Tooling cannot collect a requested metric
- **WHEN** the local environment cannot reliably collect a runtime metric
- **THEN** the baseline records the limitation and does not claim a fabricated score

### Requirement: Evidence-based backend capability audit
The project SHALL classify candidate backend capabilities against concrete repository evidence as supported, partial, frontend-only, backend-only, authorization, data-model, operational, documentation, no longer needed, or future product decision.

#### Scenario: Prior gap is reviewed
- **WHEN** a capability from an existing gap document is audited
- **THEN** its classification cites relevant routes, services, schemas, models, migrations, authorization rules, tests, consumers, or canonical documentation

### Requirement: Independently scoped future change roadmap
The project SHALL map verified larger gaps to prioritized, independently implementable future OpenSpec proposals with users, value, limitations, dependencies, security, privacy, migration, test, complexity, sequence, and beta-blocking considerations.

#### Scenario: Large capability gap is confirmed
- **WHEN** the audit confirms work beyond the narrow Phase 7 scope
- **THEN** the work is assigned to a bounded future proposal rather than implemented inside the platform-maturity foundation change

### Requirement: Platform security baseline
The project SHALL review authentication, authorization, organization scoping, object access, uploads, validation, error disclosure, browser security, secrets, sensitive logging, rate limiting, dependencies, administrative protection, and auditability, and SHALL severity-classify findings.

#### Scenario: Broad security remediation is identified
- **WHEN** a security finding requires a schema, infrastructure, policy, or major API change
- **THEN** it is documented and routed to a future OpenSpec proposal without weakening current controls

#### Scenario: Narrow security defect is fixed
- **WHEN** a low-risk compatible security defect is corrected in Phase 7
- **THEN** focused regression coverage demonstrates the corrected boundary

### Requirement: Observability and operational baselines
The project SHALL document current logging, error handling, request correlation, health behavior, database checks, metrics, tracing, privacy-safe logging, environment validation, migrations, seed safety, backup and restore assumptions, deployment, rollback, secrets, temporary QA cleanup, and dependency-update readiness.

#### Scenario: Infrastructure decision is absent
- **WHEN** an operational requirement depends on an unselected hosting or monitoring platform
- **THEN** the requirement is marked blocked by that decision rather than assigned an invented implementation

### Requirement: Dependency and code-quality review
The project SHALL inspect frontend and backend dependencies, lockfiles, production inclusion, duplication, deprecation, CommonJS usage, version pinning, reproducibility, linting, type checking, testing, and vulnerability tooling, and SHALL remove or correct only dependencies verified safe to change.

#### Scenario: Dependency appears unused
- **WHEN** static inspection identifies a potentially unused production dependency
- **THEN** repository imports, build behavior, and regression tests are checked before removal

### Requirement: Full release-quality verification
Phase 7 SHALL preserve or increase the 228 backend, 284 Angular, and 16 Playwright baselines and SHALL pass the production build, bundle analysis, strict OpenSpec validation, and `git diff --check`.

#### Scenario: Test collection decreases
- **WHEN** a required suite collects fewer tests than its Phase 6 baseline
- **THEN** Phase 7 is not considered complete until the reduction is explained and approved or the coverage is restored

#### Scenario: Verification creates temporary infrastructure
- **WHEN** local QA services or databases are used
- **THEN** they are removed after verification and their cleanup is recorded

### Requirement: Phase 6 compatibility boundary
Phase 7 SHALL leave the completed Phase 6 OpenSpec tasks unchanged and SHALL not remove or redesign public, authentication, Learn, Teach, Studio, Organization, Admin, navigation, shared state, accessibility, responsive, or authorization behavior except to correct a verified regression.

#### Scenario: Performance change affects a completed role experience
- **WHEN** a lazy-loading or dependency optimization changes a completed role route
- **THEN** existing behavior, accessibility, visual appearance, and authorization remain compatible
