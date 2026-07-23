## Context

Phase 6 completed EchoEd's role-based UI/UX overhaul and passed the full backend, Angular, Playwright, production-build, OpenSpec, and whitespace checks. Its active OpenSpec change is complete and valid but unarchived. Phase 7 begins from that committed, clean baseline and must improve platform maturity without reopening visual scope or weakening direct-route, role, organization, accessibility, or API behavior.

The Angular production build currently reports an approximately 1.42 MB initial bundle against a 1.25 MB warning budget. The frontend is a standalone-component Angular application with many eagerly imported route components. The FastAPI backend already implements substantial curriculum, progress, organization, governance, upload, discussion, and analytics behavior, so prior gap documents must be verified against code rather than accepted as product truth.

## Goals / Non-Goals

**Goals:**

- Produce reproducible bundle evidence and reduce the initial Angular bundle below the existing warning budget.
- Introduce route-level loading boundaries that preserve deep links, guards, accessible states, legacy paths, and role behavior.
- Establish measured or explicitly limitation-qualified runtime performance evidence.
- Audit backend capabilities and classify verified gaps with concrete repository references.
- Establish actionable security, observability, operational, dependency, and release-quality baselines.
- Turn larger verified gaps into sequenced future OpenSpec proposals.
- Preserve or increase the 228 backend, 284 Angular, and 16 Playwright regression baselines.

**Non-Goals:**

- Reopening the Phase 6 visual design or adding another design system.
- Implementing full authoring, review, versioning, asset-library, collaboration, analytics, billing, licensing, hierarchy, or hosting capabilities.
- Replacing Angular, FastAPI, auth, organization scoping, or existing domain models.
- Raising the bundle warning merely to suppress it.
- Claiming synthetic performance scores that were not collected.
- Selecting a hosting provider or commercial monitoring service.

## Decisions

### Use measured build statistics before changing imports

Generate Angular production statistics and inspect emitted chunks, dependency inputs, styles, assets, and route imports before selecting optimizations. Before and after artifacts will be retained as documentation evidence, while generated build output remains untracked.

Alternative considered: optimize from package reputation or intuition. Rejected because it cannot establish causality or measured size benefit.

### Prefer route-level dynamic imports as the primary bundle boundary

Convert independently navigable standalone page components from eager `component` imports to `loadComponent` dynamic imports, keeping guards and redirects on the route definitions. Group only components that truly share a navigation boundary. Add route-configuration tests that assert lazy-loader presence without depending on generated chunk names.

Alternative considered: defer individual template fragments first. Rejected as the primary approach because route-level code is the clearest noncritical boundary and avoids UI placeholders.

### Preserve behavior at route contracts

Optimization acceptance is based on direct navigation, guard enforcement, back/forward navigation, role smoke tests, accessible loading/error behavior, and visual comparison. Generated chunk names and exact byte-for-byte chunk layouts are not API contracts.

Alternative considered: snapshot emitted filenames. Rejected because hashes and optimizer partitioning are intentionally unstable.

### Separate collected measurements from code-inspection findings

Bundle output and locally supported browser timings are recorded as measurements. Metrics unavailable because of browser, server, authentication, or audit-tool limitations are marked blocked. Code-inspection recommendations are explicitly labeled as inferred.

Alternative considered: estimate Lighthouse scores from bundle size. Rejected because bundle size does not establish Core Web Vitals.

### Treat capability planning as an evidence audit

Each capability classification cites at least one concrete route, model, schema, migration, authorization rule, test, consumer, or canonical document. Large verified gaps become roadmap entries with dependencies and testing strategies, not implementation folders.

Alternative considered: copy the Phase 6 gap register into a roadmap. Rejected because several areas may already be partially supported.

### Limit security fixes to narrow compatible hardening

Phase 7 may correct low-risk configuration, validation, or documentation defects with focused tests. Findings requiring data models, product policy, infrastructure, or broad API behavior become future proposals.

Alternative considered: combine all security findings into this change. Rejected because it would obscure risk, migration, and authorization review.

### Keep baselines canonical and linked

Phase 7 documents link to existing authoritative architecture, security, and UX route documents where those remain canonical. Existing documents are updated only when measured behavior or ownership changes.

Alternative considered: duplicate all operational guidance into the Phase 7 folder. Rejected because duplicated runbooks drift.

## Risks / Trade-offs

- [Lazy loading exposes hidden circular imports or missing direct imports] → Build after each route group, retain direct-route tests, and roll back individual route conversions.
- [More chunks increase requests on slow connections] → Compare initial and lazy chunk output, avoid excessively granular splitting, and preserve shared chunks.
- [A smaller bundle regresses navigation or accessibility] → Run full unit, role, keyboard, responsive, and visual suites and inspect loading semantics.
- [Authenticated runtime measurements vary with seeded data and machine load] → Record environment and methodology, use repeatable samples where supported, and avoid unsupported scores.
- [Gap classifications become stale] → Cite repository paths and commit baseline, and route each implementation through its own future OpenSpec validation.
- [Security documentation reveals sensitive operational details] → Describe controls and gaps without recording secrets, tokens, or exploitable production data.
- [Phase 6 remains active while Phase 7 starts] → Record the unarchived status, never edit its tasks, and keep Phase 7 artifacts isolated.

## Migration Plan

1. Capture the clean committed baseline and before-build statistics.
2. Add Phase 7 artifacts and strict validation.
3. Introduce lazy route boundaries in small groups with unit/build checks.
4. Apply only verified dependency/style/asset optimizations, recording individual effects.
5. Run direct-route and full regression verification against seeded local services.
6. Publish audit and roadmap documents with evidence and limitations.
7. Remove temporary build-analysis files, QA services, and databases.

Rollback is per route or dependency optimization. Because Phase 7 plans no schema migration, rollback restores eager imports or the prior dependency/style implementation without data reversal.

## Open Questions

- Hosting-specific readiness, backup, restore, edge caching, and monitoring choices remain blocked until a deployment target is selected.
- Performance targets beyond the existing bundle budget require production traffic profiles and supported-device goals.
- The future proposal sequence may change after security, privacy, and product owners review the evidence-based roadmap.
