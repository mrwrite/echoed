## Why

EchoEd already has working authentication, organization, onboarding, and role-aware shell foundations, but several of the most failure-prone flows still depend on duplicated frontend decisions, ambiguous active-organization assumptions, and inconsistent bootstrap timing. Before further institutional expansion, these seams need to become deterministic so login, onboarding, org switching, permissions, and first authenticated paint behave the same way every time.

This initiative is implementation-oriented hardening work. It preserves the current architecture and current auth, org, and permission services, but it makes them authoritative enough to support the broader platform-hardening and institutional-evaluation roadmap already underway.

## What Changes

- Establish one canonical authority for active-organization resolution, including deterministic selection, personal-versus-institutional handling, server-confirmed switching, and role reconciliation
- Define one canonical frontend session bootstrap path so guards, home/dashboard entry points, and the shared shell hydrate session, organization, and permissions state through the same flow
- Normalize auth token handling and login response expectations so interceptors, protected requests, invalid-token behavior, and post-login state resolution follow a consistent contract
- Centralize onboarding-required evaluation so login, guard redirects, and first authenticated navigation do not drift across users with no orgs, personal-only orgs, pending setup, or valid active organizations
- Require organization switching to update frontend state only from server-confirmed active-org and role context rather than optimistic local assumptions
- Stabilize shell and navigation first-paint behavior so sidebar, dashboard, permissions, and role-aware navigation do not flash or render from unresolved session state
- Add regression coverage for login bootstrap, onboarding redirects, active-org selection, org-switch confirmation, permission hydration, and shell/dashboard readiness
- Keep all work inside the current EchoEd architecture without introducing auth rewrites, parallel session systems, or disconnected org-state flows

## Capabilities

### New Capabilities
- `auth-org-session-authority`: Canonical requirements for active organization, auth token handling, onboarding decisions, session bootstrap, and organization switching authority
- `shell-bootstrap-and-navigation-readiness`: Canonical requirements for first authenticated paint, role-aware shell rendering, dashboard readiness, and navigation stability after bootstrap
- `auth-org-session-hardening-verification`: Regression coverage requirements for the hardening flows introduced by this initiative

### Modified Capabilities
- None

## Impact

- Frontend:
  - Consolidates bootstrap and redirect logic across auth services, guards, home entry, dashboard entry, and shared shell rendering
  - Removes reliance on `organizations[0]` assumptions and other local org-state shortcuts
  - Stabilizes permission hydration, navigation rendering, and authenticated first-paint behavior

- Backend:
  - Clarifies authoritative login and organization-switch response contracts
  - Reuses existing auth, org, and permission services rather than creating replacements
  - Strengthens invalid-token, active-org, and role-context consistency where current route behavior is ambiguous

- Testing:
  - Adds focused backend and frontend regression protection for the exact flows most likely to break during future institutional expansion

- Strategic Alignment:
  - Directly supports `echoed-platform-foundation-hardening`
  - Provides a narrower implementation track that supports `echoed-global-education-platform-evaluation`
  - Creates a dependable auth, organization, and shell baseline for later institutional capabilities
