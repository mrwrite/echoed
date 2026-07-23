## Why

The role-based UI/UX overhaul is complete, but EchoEd still needs measured performance work and evidence-based security, operational, observability, dependency, and backend-capability planning before a credible 1.0 release process can begin. Phase 7 establishes that platform-maturity foundation without reopening the completed visual design or bundling every future backend capability into one implementation change.

## What Changes

- Measure the Angular production bundle and runtime behavior, then reduce the initial bundle below the existing 1.25 MB warning budget through compatible loading and dependency optimizations.
- Preserve direct navigation, guards, authorization boundaries, accessible loading behavior, legacy route compatibility, and all completed role experiences while improving route-level loading architecture.
- Audit actual backend routes, models, schemas, migrations, authorization rules, tests, and frontend consumers before classifying capability gaps.
- Convert verified larger gaps into an evidence-based, prioritized roadmap of independent future OpenSpec proposals rather than implementing them in Phase 7.
- Establish documented security, observability, operational-readiness, dependency, code-quality, and release-verification baselines.
- Apply only narrow, low-risk fixes that are directly supported by audit evidence and do not require broad product behavior or schema changes.
- Record reproducible before/after measurements, environment limitations, full regression results, and rollback considerations.
- Do not simulate unsupported capabilities in the frontend, weaken security or organization scoping, remove role functionality, or introduce a visual redesign.

## Capabilities

### New Capabilities

- `platform-maturity-foundation`: Defines the measured frontend performance, route-loading compatibility, evidence-based capability audit, security and operational baselines, future-change planning, and release-quality verification required by Phase 7.

### Modified Capabilities

None.

## Impact

- Frontend: Angular route configuration, feature loading boundaries, production dependencies, build output, and stable performance/regression tests.
- Backend: read-only capability and security inspection plus only narrowly justified low-risk hardening; no planned database migration or broad new capability.
- Documentation: new canonical `docs/platform-maturity/` audit, baseline, roadmap, implementation, and verification documents plus links or factual updates to existing canonical project documents.
- OpenSpec: one scoped Phase 7 implementation change and a roadmap of separately proposed future changes; the completed Phase 6 task file remains untouched.
- Compatibility: current APIs, direct routes, role navigation, accessibility behavior, and organization authorization boundaries remain supported.
