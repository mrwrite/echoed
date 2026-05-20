## Why

EchoEd now has a deterministic seeded demo environment, but it still lacks a browser-level confidence check that proves the flagship demo experience works end to end through the real UI. A bounded smoke layer is needed so operators can validate the live demo path quickly without introducing a heavy E2E program or product-specific test hacks.

## What Changes

- Add a lightweight Playwright smoke-validation layer for the seeded EchoEd demo environment.
- Cover bounded student, teacher, and admin walkthroughs centered on the flagship "Introduction to Africa" course.
- Add deterministic browser helpers, selectors, and failure output focused on demo reliability rather than exhaustive regression coverage.
- Add operator documentation for how to run the demo smoke flow and interpret failures.

## Capabilities

### New Capabilities
- `deterministic-demo-smoke-execution`: Run a repeatable, demo-safe browser smoke flow against the seeded demo environment with bounded retries and clear failure output.
- `flagship-student-smoke-validation`: Validate the flagship student path from login through governed lesson and assessment loading.
- `flagship-staff-smoke-validation`: Validate teacher and admin dashboard smoke coverage for governance, runtime recommendations, and runtime support surfaces.
- `demo-operational-confidence-checks`: Document and enforce bounded operational checks that prove demo readiness without expanding into a full E2E suite.

### Modified Capabilities

None.

## Impact

- Affected code: `frontend/playwright/*`, `playwright.config.ts`, and `docs/demo-smoke-validation.md`
- Affected systems: browser smoke tooling, demo operator workflow, and seeded demo validation coverage
- No backend architecture changes, governance redesign, workflow additions, route changes, or seed redesign
