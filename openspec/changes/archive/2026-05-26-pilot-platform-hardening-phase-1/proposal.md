## Why

EchoEd is past the point where functional MVP behavior is enough. The current platform can already demonstrate governed learning, student progression, and teacher visibility, but small real-world pilot usage will expose instability in shell bootstrap, dashboard state rendering, lesson continuation, runtime edge cases, and demo/operator confidence if those seams are not hardened now.

This phase matters because pilot trust is won or lost through the first few visible interactions: logging in, seeing the right dashboard state, entering a lesson, recovering from transient failures, and reseeding a deterministic demo without hidden repair work. Phase 1 focuses on those reliability and polish gaps before larger feature investments.

## What Changes

- Harden the authenticated shell so header, sidebar, dashboard entry, and lesson return paths render from resolved role and organization state without visible instability
- Improve the student dashboard and lesson runtime experience so the active course path, continuation entry, governed blocked states, and return-to-dashboard flow remain readable and safe
- Improve the teacher dashboard baseline so pilot demos consistently show enough course, learner, and runtime state to narrate platform value without dead panels or ambiguous empty states
- Standardize user-friendly loading, error, blocked, and empty states across the student dashboard, teacher dashboard, lesson runtime, and shell-adjacent flows
- Fix obvious accessibility defects in pilot-critical flows, especially contrast, focus order, labels, and keyboard-safe navigation through shell and lesson actions
- Verify backend progression and runtime routes continue to enforce governed delivery correctly while preserving ordinary non-governed sequential advancement behavior
- Keep demo seeding deterministic and strengthen demo/smoke operational documentation so pilot prep is reproducible
- Tighten basic operational confidence checks across backend pytest, frontend Angular tests, student Playwright smoke coverage, and CI workflow expectations

## User-Visible Problems Addressed

- Student login can reach a dashboard or lesson flow that feels visually unstable or underexplained while async data resolves
- Teacher login can surface sparse, inconsistent, or low-confidence dashboard sections during a live walkthrough
- Lesson entry and exit can feel fragile if governed, unavailable, or retry states are not clearly communicated
- Shared shell/header/sidebar behavior can show avoidable layout shifts, incomplete loading states, or ambiguous role-aware navigation
- Core surfaces can still expose contrast, readability, or empty-state defects that reduce pilot confidence even when underlying data is correct
- Demo preparation can drift if seeded users, seeded relationships, smoke steps, or validation docs are not deterministic

## Out of Scope

- New major product features, new pedagogical workflows, or broad information architecture changes
- Replacing the current authentication, organization, or governance architecture
- Large redesign work across all pages, visual rebranding, or full design-system replacement
- New analytics, telemetry vendors, or production observability platforms
- Expanded multi-role end-to-end smoke coverage beyond bounded pilot-confidence checks unless already necessary for Phase 1 acceptance

## Risks and Mitigations

- Broad "polish" work can sprawl into redesign: mitigate by limiting work to pilot-critical student, teacher, shell, and lesson-runtime flows
- UI hardening can hide backend inconsistencies instead of exposing them: mitigate by pairing frontend fixes with backend/runtime verification and existing test coverage
- Demo-confidence work can accidentally weaken production guardrails: mitigate by preserving real auth, real governed progression, and deterministic seeding through production logic only
- CI additions can become noisy and expensive: mitigate by keeping checks bounded to existing backend pytest, Angular tests, and the current student smoke path

## Verification Strategy

- Keep `backend` pytest green, including progression/runtime and demo-seed coverage
- Keep existing Angular component/unit tests green for shell, student dashboard, teacher dashboard, and lesson runtime surfaces
- Keep the existing student Playwright smoke flow green for login, active-course discovery, lesson entry, and safe lesson exit/return expectations
- Document bounded manual pilot verification for student and teacher core flows where automation does not yet exist
- Confirm no production auth behavior is weakened and demo seed remains deterministic across repeat runs

## Capabilities

### New Capabilities
- `pilot-operational-confidence-checks`: bounded pilot-readiness validation across smoke checks, CI expectations, and operator verification steps

### Modified Capabilities
- `shell-bootstrap-and-navigation-readiness`: stabilize role-aware shell, header, sidebar, and dashboard entry/return behavior during authenticated bootstrap
- `learner-experience-hardening`: strengthen student dashboard continuation, lesson entry, governed blocked handling, and safe return behavior
- `educator-experience-hardening`: strengthen teacher dashboard baseline visibility, responsive layout, and recovery states for pilot demonstrations
- `canonical-ux-state-system`: require consistent loading, error, blocked, and empty-state rendering across pilot-critical flows
- `accessibility-and-global-readiness`: tighten contrast, focus, keyboard, and readable-state expectations in core student/teacher flows
- `governed-progression-integrity`: preserve governed progression safety while preventing stale draft activation and keeping ordinary non-governed advancement intact
- `deterministic-demo-foundation`: guarantee demo users and seeded relationships reset deterministically without duplicate rows
- `demo-reset-and-operational-readiness`: tighten demo prep, smoke-validation, and manual verification runbooks for pilot operators

## Impact

- Frontend:
  - `frontend/src/app/pages/user-dashboard/**`
  - `frontend/src/app/pages/lesson-view.component.*`
  - `frontend/src/app/shared/lesson-viewer.component.*`
  - `frontend/src/app/components/echo-header/**`
  - `frontend/src/app/components/echo-sidebar/**`
  - shared loading/error/empty-state components and styles
- Backend:
  - progression/runtime route coverage and related service logic
  - demo seed determinism and operator validation expectations
- Testing and operations:
  - existing backend pytest suite
  - existing Angular tests
  - existing Playwright student smoke flow
  - CI workflow expectations
  - demo readiness and smoke validation documentation
