## 1. Scope and Flow Audit

- [x] 1.1 Review `echoed-platform-foundation-hardening` and `echoed-global-education-platform-evaluation` artifacts to confirm this change remains a focused hardening implementation track
- [x] 1.2 Audit current backend and frontend ownership of login response handling, token persistence, active organization selection, onboarding-required decisions, and shell bootstrap
- [x] 1.3 Identify every duplicate bootstrap or redirect path currently split across guard, home entry, dashboard entry, and shared shell rendering

## 2. Canonical Active Organization Authority

- [x] 2.1 Define the deterministic active-organization selection rules for no-org, personal-only, institutional, and mixed-membership users
- [x] 2.2 Normalize the backend contract for active-organization and role-context confirmation during login and org switching
- [x] 2.3 Refactor frontend org-state updates so they are driven only by canonical server-confirmed responses
- [x] 2.4 Remove or replace frontend assumptions based on `organizations[0]` and similar local shortcuts

## 3. Canonical Session Bootstrap

- [x] 3.1 Designate one frontend bootstrap path as the canonical authenticated-entry flow
- [x] 3.2 Refactor guards, home entry, dashboard entry, and any shell bootstrap hooks to consume the same canonical bootstrap outcome
- [x] 3.3 Ensure session bootstrap resolves user, active organization, onboarding-required status, and permissions in a stable sequence
- [x] 3.4 Remove duplicate bootstrap logic that rehydrates equivalent session or org state in parallel

## 4. Auth and Token Consistency

- [x] 4.1 Audit token attachment paths and identify any manual authorization header construction that duplicates interceptor behavior
- [x] 4.2 Normalize login response parsing so downstream authenticated flows consume one stable contract
- [x] 4.3 Harden invalid-token and expired-token handling so partial authenticated UI states do not persist
- [x] 4.4 Keep existing auth services in place while consolidating contract ownership

## 5. Onboarding Determinism

- [x] 5.1 Centralize onboarding-required evaluation for no-org, personal-only, pending-setup, and valid-active-org states
- [x] 5.2 Align login redirect behavior and guarded-route redirect behavior to the same onboarding decision
- [x] 5.3 Eliminate silent fallthrough to `/home` when organization lookup fails or yields no usable destination
- [x] 5.4 Preserve current onboarding architecture while removing conflicting route-local interpretations

## 6. Organization Switching Reliability

- [x] 6.1 Refactor organization switching to avoid optimistic local active-org updates before server confirmation
- [x] 6.2 Ensure confirmed switch responses provide the authoritative active-org and role context needed by the frontend
- [x] 6.3 Refresh dependent permission and navigation state only from the confirmed switch outcome
- [x] 6.4 Define failure handling so rejected org switches preserve the prior stable session context

## 7. Shell and Navigation Stability

- [x] 7.1 Gate shared shell rendering on resolved session, org, and permission readiness
- [x] 7.2 Eliminate sidebar, role, and navigation flash on first authenticated paint
- [x] 7.3 Stabilize dashboard rendering so post-bootstrap entry is consistent across login, refresh, and org-switch flows
- [x] 7.4 Standardize loading and unavailable states for unresolved or unusable authenticated entry outcomes

## 8. Verification

- [x] 8.1 Add tests for login bootstrap outcomes
- [x] 8.2 Add tests for onboarding redirect behavior
- [x] 8.3 Add tests for deterministic active-organization selection
- [x] 8.4 Add tests for server-confirmed organization switching
- [x] 8.5 Add tests for permission bootstrap and shell readiness on first paint
- [x] 8.6 Verify the hardening keeps EchoEd on one canonical session flow without introducing rewrites or a parallel session system

## Follow-Ups

- [ ] Consider adding explicit public-endpoint opt-out behavior for `authInterceptor` if public endpoints should avoid bearer headers
- [ ] Review whether `orgInterceptor` should use an allowlist for org-scoped endpoints instead of attaching `X-Org-Id` globally
- [ ] Consider moving post-switch permission refresh ownership fully into `OrganizationService` or a session orchestration helper
- [ ] Continue monitoring any authenticated components reused outside the guarded shell to ensure they also follow canonical readiness contracts