## Context

EchoEd already demonstrates the core ingredients needed for a pilot: authenticated role-aware dashboards, governed lesson delivery, student progression, teacher visibility, deterministic demo seed data, backend regression coverage, and a bounded Playwright smoke path. The current weakness is not missing platform concepts; it is uneven operational confidence in the seams between them.

The sampled codebase reflects that shape clearly:

- the student dashboard already has continuation cards and canonical state components, but its pilot trust depends on stable async behavior and safe lesson transitions
- the teacher dashboard already exposes meaningful governance and runtime surfaces, but it is dense and vulnerable to low-confidence loading, empty, and responsive states
- the lesson runtime already exposes governed blocked/error handling, but return-to-dashboard and recovery flows must stay deterministic
- the shared shell/header/sidebar remain critical because every pilot role experiences them first
- the backend runtime and progression layer must keep governed safety intact while still preserving ordinary sequential progression
- demo readiness currently depends on deterministic seed behavior plus operator docs and bounded smoke checks

This phase is therefore a cross-cutting hardening pass, not a feature program.

## Goals / Non-Goals

**Goals:**

- Make student and teacher first-run authenticated experiences feel stable enough for real pilot walkthroughs
- Preserve deterministic lesson continuation, governed blocked handling, and safe lesson exit/return behavior
- Eliminate obvious loading, error, empty-state, and readability defects in pilot-critical flows
- Keep governed progression and runtime behavior safe while locking in regression coverage
- Strengthen demo/operator confidence through deterministic seed behavior, bounded smoke checks, and clearer runbooks
- Increase confidence in CI without redesigning the whole workflow

**Non-Goals:**

- New product workflows, new reporting systems, or new learning features
- Replacing the current shell, auth, organization, or governance architecture
- Broad visual redesign or design-language replacement
- Full observability platform adoption or production incident tooling
- End-to-end automation of every pilot scenario

## Decisions

### Frontend hardening strategy

Pilot hardening will stay inside the existing Angular shell, dashboard, and lesson-view structure. The implementation should avoid introducing parallel layout or routing systems. Instead, Phase 1 should:

- audit the shared shell, header, and sidebar for unstable first paint, layout shift, hidden controls, and weak route transitions
- normalize student and teacher dashboard data-fetch entry states around the existing canonical loading and state-panel components
- preserve the current student "active course -> continue lesson -> lesson route -> return to dashboard" path as the primary pilot learner story
- preserve the current teacher dashboard as a bounded read-mostly pilot surface, emphasizing stable visibility and recovery over broader feature expansion

Alternative rejected: a broader dashboard redesign. That would increase polish in some places, but it would not improve pilot confidence as efficiently as stabilizing the existing surfaces.

### Backend and runtime hardening strategy

Backend hardening will focus on verification and small correctness fixes in progression/runtime behavior, not new service families. The governing rule is:

- governed learner delivery must never auto-activate stale draft or non-governed progress rows
- ordinary non-governed progression must still advance to the next `NOT_STARTED` segment as expected

Phase 1 should favor targeted reinforcement of existing progression helpers, governed filtering decisions, and regression tests around runtime endpoints instead of larger refactors.

Alternative rejected: central progress-model redesign. That would be too large for a pilot hardening phase and would risk destabilizing already-green behavior.

### Accessibility and contrast approach

This phase will apply a baseline accessibility pass only to pilot-critical surfaces:

- authenticated shell
- student dashboard
- teacher dashboard
- lesson runtime
- shared loading/error/empty-state surfaces

The pass should cover contrast, readable hierarchy, keyboard order, actionable labels, focus visibility, and state announcements where async transitions change the meaning of the page. This is intentionally narrower than a platform-wide accessibility remediation program.

Alternative rejected: page-by-page full WCAG certification effort. That is appropriate later, but not necessary to achieve Phase 1 pilot readiness.

### Error, loading, and empty-state approach

The platform already has canonical state components. Phase 1 should standardize when and how they are used:

- loading states should explain what is being prepared and avoid leaving stale content ambiguously visible
- error states should explain the failed surface in user language and offer retry or return actions where valid
- empty states should distinguish "no data yet" from blocked or failed outcomes
- governed blocked states should stay semantically distinct from generic failures

Alternative rejected: route-local custom placeholders. They make short-term implementation easy, but they fragment the runtime experience and reduce pilot trust.

### Observability and logging approach

Phase 1 will not add a new telemetry stack. It will add bounded operational confidence instead:

- keep backend assertions and regression tests authoritative for progression and seed determinism
- use existing API error responses and route behavior as the main reliability signal
- document operator-visible failure points in demo and smoke runbooks
- where lightweight logging is needed, prefer structured application logs around seed, bootstrap, and governed runtime failure paths over noisy debug output

Alternative rejected: adding a full observability vendor during a hardening pass. That expands operational surface area without directly improving the pilot experience.

### Smoke-test and CI confidence approach

CI confidence should remain bounded and legible:

- backend pytest remains the main authority for runtime and seed correctness
- existing Angular tests remain the main authority for component-level regression coverage
- the existing student Playwright smoke remains the browser-level pilot-confidence check
- docs should define a manual student and teacher pilot walkthrough when automation is intentionally absent
- CI should stay simple: keep the current backend and frontend jobs green, and document any smoke execution expectations separately unless CI expansion is explicitly justified

Alternative rejected: turning this phase into a large CI redesign. The immediate need is confidence, not pipeline complexity.

## Risks / Trade-offs

- Cross-cutting polish changes can create hidden regressions in adjacent routes
  - Mitigation: bias toward existing shared state components, existing test suites, and bounded route changes
- Teacher dashboard hardening can drift into feature expansion because the surface is already broad
  - Mitigation: treat the teacher dashboard as a baseline pilot narrative surface, not a new educator product initiative
- Accessibility fixes can expose component-level inconsistencies across the shell and dashboard stack
  - Mitigation: focus on high-signal defects first: contrast, focus order, labels, and keyboard-safe actions
- Smoke confidence can be overstated if docs and automation diverge
  - Mitigation: keep the smoke path intentionally narrow and document exactly what it does and does not prove

## Migration Plan

No production data migration is expected for this phase. Rollout is code-first and validation-first:

1. land backend/runtime safety fixes and regression tests
2. harden shell, student, teacher, and lesson surfaces behind existing routes
3. refresh demo/operator docs and bounded smoke expectations
4. verify backend pytest, Angular tests, and the current student smoke path

Rollback remains straightforward because this phase should not introduce new persistence models or alternate auth/governance paths.

## Open Questions

- Should the existing student smoke be expanded to assert safe return from lesson to dashboard in Phase 1, or is documented manual verification sufficient for that last step?
- Is there already a preferred lightweight structured logging pattern in backend runtime routes that this phase should reuse for governed/unavailable outcomes?
- Should the current CI workflow stay limited to backend pytest and Angular tests for now, with Playwright remaining operator-invoked, or is there appetite to promote the student smoke into CI in a later hardening phase?
