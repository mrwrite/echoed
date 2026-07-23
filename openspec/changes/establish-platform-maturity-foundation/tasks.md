## 1. Baseline and Evidence

- [x] 1.1 Record the branch, commit, clean working-tree baseline, Phase 6 strict-validation and archive status, existing test baselines, bundle budget, gap documents, and security/operations documentation in `docs/platform-maturity/phase-7-baseline.md`.
- [x] 1.2 Generate an Angular production build with statistics and document initial/lazy/shared chunks, largest JS and CSS inputs, assets, fonts, build settings, dependency duplication, eager routes, and evidence-backed optimization candidates in `frontend-performance-audit.md`.
- [x] 1.3 Collect reproducible representative-route runtime observations where the environment supports them, and document blocked metrics separately from code-inspection recommendations in `runtime-performance-baseline.md`.

## 2. Frontend Performance Implementation

- [x] 2.1 Convert suitable public, authentication, onboarding, Learn, Teach, Studio, Organization, and Admin routes to guarded standalone lazy-loading boundaries while preserving redirects and direct deep links.
- [x] 2.2 Add stable route-loading and chunk-failure recovery coverage without asserting generated chunk filenames.
- [x] 2.3 Remove or correct only verified unused/heavy imports, production dependencies, duplicated styles, assets, or font-loading behavior supported by measured evidence.
- [x] 2.4 Rebuild with statistics, confirm the initial bundle is at or below 1.25 MB without changing the warning budget, and document each measured optimization and rollback consideration in `frontend-performance-implementation.md`.
- [x] 2.5 Update `docs/ux-overhaul/production-route-migration.md` only for actual route-loading changes.

## 3. Platform Capability and Risk Audits

- [x] 3.1 Audit content authoring, editorial workflow, assets/sources, teacher, organization, and platform capabilities against routes, models, schemas, migrations, authorization, tests, consumers, and prior documents in `backend-capability-audit.md`.
- [x] 3.2 Create a prioritized, dependency-aware future proposal map with independent scopes, security/privacy/migration/testing considerations, beta impact, and recommended sequence in `future-openspec-roadmap.md`.
- [x] 3.3 Complete and severity-classify the focused authentication, authorization, organization-scope, upload, validation, browser-security, secrets, logging, rate-limit, dependency, and administrative-action review in `security-baseline.md`.
- [x] 3.4 Audit logging, errors, request correlation, health/readiness, database visibility, metrics, tracing, event logging, and privacy-safe redaction in `observability-baseline.md`.
- [x] 3.5 Audit configuration, migrations, seed safety, backup/restore, deployment/rollback, health verification, assets, secrets, QA cleanup, data safeguards, scheduled work, and dependency updates in `operational-readiness-baseline.md`.
- [x] 3.6 Audit frontend/backend dependency use, duplication, deprecation, production inclusion, version pinning, lockfiles, reproducibility, lint/type checking, and vulnerability tooling in `dependency-review.md`.

## 4. Scoped Hardening and Canonical Documentation

- [x] 4.1 Implement and test only narrow, low-risk performance, security, observability, dependency, or configuration fixes proven necessary by the audits.
- [x] 4.2 Update `backend-gap-register.md`, `README.md`, `ROADMAP.md`, `ARCHITECTURE.md`, and `SECURITY.md` only where Phase 7 evidence changes canonical guidance, linking rather than duplicating.

## 5. Full Verification and Handoff

- [x] 5.1 Run the complete backend suite and confirm at least the 228-test baseline with no unexplained collection reduction.
- [x] 5.2 Run the complete Angular suite and confirm at least the 284-test baseline with route-loading coverage.
- [x] 5.3 Run all Playwright smoke, authorization, keyboard, responsive, direct-route, and visual-regression coverage and confirm at least the 16-test baseline.
- [x] 5.4 Run the production build, final bundle analysis, strict Phase 7 OpenSpec validation, and `git diff --check`; verify no original bundle warning or undocumented new warning remains.
- [x] 5.5 Record all before/after measurements, regression counts, environment limitations, known limitations, cleanup, and completion status in `phase-7-verification.md`, then remove temporary QA services, databases, and generated analysis artifacts.
