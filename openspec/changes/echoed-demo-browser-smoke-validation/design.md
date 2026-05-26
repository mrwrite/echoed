## Context

EchoEd already has deterministic backend seed data, staff governance verification, and frontend dashboard behavior validated through unit and API-level tests. What is missing is a browser-level smoke layer that proves the flagship seeded demo works through the real auth flow and visible student, teacher, and admin surfaces. This change must stay intentionally small: it should increase demo confidence, not become a broad E2E framework or redesign the existing Playwright setup into a large CI system.

## Goals / Non-Goals

**Goals:**
- Validate seeded demo readiness through a small number of deterministic browser flows.
- Exercise real login and session behavior for student, teacher, and admin demo accounts.
- Verify the flagship course path renders correctly for learner and staff demo stories.
- Keep smoke execution time bounded and failure output understandable for operators.
- Reuse the existing seeded demo environment and current product behavior without adding test-only business logic.

**Non-Goals:**
- Full end-to-end coverage of the platform
- Visual regression or screenshot baselining
- Performance or load benchmarking
- Backend mutation orchestration beyond normal user actions already in the product
- Governance redesign, seed redesign, or workflow expansion
- CI pipeline redesign

## Decisions

### Use one bounded browser smoke layer instead of a broad E2E suite

The smoke flow will cover only the deterministic flagship demo paths that operators actually need before a live demo: environment readiness, student walkthrough, teacher walkthrough, and admin walkthrough.

Alternatives considered:
- Expand into general E2E coverage: rejected because it would increase maintenance cost and scope quickly.
- Keep only backend and component tests: rejected because they do not prove real browser/auth/session behavior.

### Reuse seeded demo identities and course state exactly as they already exist

The browser smoke layer will target the canonical seeded accounts and the flagship "Introduction to Africa" course instead of creating test-only fixtures or alternate data paths.

Alternatives considered:
- Create browser-specific seed data: rejected because it would diverge from the demo operators' real environment.
- Mock auth or dashboard data: rejected because it would weaken demo confidence and production alignment.

### Prefer deterministic selectors and stable text anchors over brittle visual structure

The implementation should use deterministic selectors where available and add bounded test hooks only if needed. Where hooks do not already exist, stable semantic headings, labels, and section text should be preferred over fragile layout selectors.

Alternatives considered:
- Rely on incidental CSS structure: rejected because it is brittle during UI polish.
- Add broad testing-only instrumentation everywhere: rejected because it would overcomplicate the product for a smoke-only need.

### Keep retries bounded and failure output operator-oriented

The smoke flow should retry only where the real app may need short stabilization, such as initial load transitions. Failures should clearly identify which role, screen, and expected section failed so demo operators can recover quickly.

Alternatives considered:
- No retries at all: rejected because it would make the smoke layer noisy for transient load timing.
- Aggressive retry loops: rejected because they would hide real defects and extend demo prep time.

## Risks / Trade-offs

- [Selectors may be brittle in a polished but evolving UI] -> Prefer semantic anchors first and add only minimal deterministic hooks where necessary.
- [Smoke tests may become too broad over time] -> Keep capability scope explicitly bounded to demo confidence checks and avoid adding general product coverage here.
- [Real login and seeded state create setup dependencies] -> Document the required reseed and startup path clearly in demo smoke documentation.
- [Teacher/admin dashboards have dense content] -> Validate presence of the key demo-safe sections rather than every visual detail.

## Migration Plan

1. Add the Playwright smoke helpers and bounded role-based flows.
2. Add operator documentation for running the smoke layer after demo reseed.
3. Verify smoke execution against the seeded environment locally before treating it as demo-ready validation.
4. Keep rollback simple by removing the added smoke specs and docs if needed; no data migration or backend migration is involved.

## Open Questions

- Which existing frontend views already expose stable selectors, and where are minimal additive hooks justified?
- Should the smoke command target one serial flagship flow or separate role-based specs with shared setup utilities?
- What is the strictest acceptable wall-clock runtime for a pre-demo smoke pass on the current local environment?
