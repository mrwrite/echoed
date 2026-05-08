## Context

EchoEd's current authentication and organization flow already has the right major pieces: login, token persistence, organizations, active organization state, permission-aware navigation, onboarding, and a shared authenticated shell. The instability comes from ownership drift. Active-organization selection, onboarding-required evaluation, and session bootstrap appear to be interpreted in multiple places across frontend guards, home or dashboard entry, shell rendering, and backend response handling.

That drift creates the exact failures this initiative is meant to remove:

- active organization inferred from `organizations[0]` or other frontend assumptions
- local org switching before server confirmation
- permissions or navigation rendering before canonical session context resolves
- duplicated bootstrap paths in guard, home, and dashboard flows
- inconsistent redirect behavior when users have no orgs, only personal orgs, or incomplete setup
- inconsistent token and login response handling across interceptors and manual request paths

This design keeps the current EchoEd architecture intact. It hardens the seams by choosing one canonical authority for auth, active organization, onboarding-required decisions, and first authenticated render.

## Goals / Non-Goals

**Goals:**

- Define one canonical post-auth bootstrap path for frontend authenticated entry
- Make backend-confirmed active-organization context the only source of truth for org switching and post-login org state
- Centralize onboarding-required evaluation so login, guards, and shell routing do not diverge
- Normalize token handling and eliminate duplicate manual authorization behavior where interceptors already own the concern
- Prevent role or navigation flash on first paint by requiring shell rendering to wait for resolved session, org, and permission state
- Add focused regression coverage for the hardening flows called out in the proposal
- Stay aligned with `echoed-platform-foundation-hardening` and `echoed-global-education-platform-evaluation`

**Non-Goals:**

- Replacing the current auth architecture
- Introducing a new session store or a parallel session system
- Rewriting organization membership, permissions, or onboarding into new service families
- Redesigning the app shell, dashboard, or navigation model
- Broadly reworking unrelated curriculum, governance, lesson, or analytics flows

## Decisions

### Decision: active organization is server-authoritative

The platform will treat active organization as backend-confirmed state rather than a frontend-derived preference. Login bootstrap and explicit organization switching will resolve active organization, authoritative role context, and any related permission implications from the server response before frontend state updates.

Rationale:

- This removes drift caused by local assumptions about org ordering or org type.
- It makes personal-org versus institutional-org handling explicit instead of incidental.
- It ensures role reconciliation happens from the same source used by protected backend routes.

Alternatives considered:

- Continue deriving active org from available org arrays on the client. Rejected because it preserves nondeterminism and `organizations[0]` coupling.
- Introduce a separate frontend session authority layer. Rejected because it creates a parallel system and violates the stated constraints.

### Decision: frontend authenticated entry uses one bootstrap pipeline

The frontend will have a single canonical bootstrap flow that resolves token validity, authenticated user state, active organization, onboarding-required status, and permissions before the shared shell or role-aware destinations treat the session as ready. Guards, home entry, and dashboard entry will delegate to the same bootstrap outcome rather than each implementing their own partial hydration logic.

Rationale:

- One flow eliminates duplicate bootstrap logic and conflicting first-load behavior.
- Shared readiness semantics make it possible to prevent first-paint flashes and role drift.
- Centralized resolution improves testability because one pipeline owns the edge cases.

Alternatives considered:

- Keep separate bootstrap paths tuned to each route type. Rejected because it perpetuates inconsistency and increases regression risk.
- Let the shell render immediately and patch in org or permissions later. Rejected because it causes nav flash and ambiguous first paint.

### Decision: onboarding-required is a canonical derived state

Onboarding-required will be evaluated through one shared rule that considers no-org, personal-only, pending setup, and valid active-organization states. Redirect behavior after login, refresh, and guarded navigation will consume that one decision.

Rationale:

- It removes silent fallthroughs to `/home` when org lookup fails or returns a non-usable context.
- It clarifies how personal orgs differ from institutional readiness.
- It keeps routing behavior consistent across login and protected-route recovery.

Alternatives considered:

- Leave onboarding checks distributed across registration, login callbacks, and guards. Rejected because the same user can be interpreted differently depending on entry point.

### Decision: token handling remains interceptor-first

Token attachment and invalid-token recovery will follow one normalized contract. Where request interceptors already own authorization behavior, application code should not manually reconstruct authorization headers unless a truly exceptional integration requires it.

Rationale:

- Centralized token behavior reduces drift between request paths.
- Invalid or expired token behavior becomes easier to reason about and test.
- Normalized login response handling prevents downstream code from compensating for inconsistent shapes.

Alternatives considered:

- Permit mixed manual and interceptor-based token logic. Rejected because it preserves hidden inconsistencies and weakens invalid-token handling.

### Decision: shell readiness gates role-aware rendering

The authenticated shell will distinguish between unresolved bootstrap and ready session state. Sidebar, dashboard, and role-aware navigation will render from resolved org and permission context only, with explicit loading or unavailable states for unresolved or unusable outcomes.

Rationale:

- This prevents role or nav flash on first paint.
- It keeps dashboard rendering aligned with resolved permissions and active org.
- It gives first-load, refresh, and post-switch behavior one visible contract.

Alternatives considered:

- Continue rendering optimistic navigation and correcting it later. Rejected because it degrades trust and makes auth-state bugs harder to diagnose.

## Risks / Trade-offs

- [Centralizing bootstrap may expose hidden dependencies] -> Mitigation: document the canonical readiness contract and add regression coverage around each current entry path.
- [Backend response normalization may surface existing frontend assumptions] -> Mitigation: preserve current architecture while tightening contracts incrementally and updating consumers in the same hardening pass.
- [Waiting for resolved session state can lengthen perceived first paint] -> Mitigation: use clear intermediate loading states and prefer one stable paint over multiple corrective re-renders.
- [Org-role reconciliation can reveal data or permission inconsistencies] -> Mitigation: treat server-confirmed org and role context as authoritative and cover role transitions in tests.

## Migration Plan

1. Identify the current frontend and backend bootstrap, login, org-switch, permission, and onboarding decision points.
2. Consolidate backend response contracts for login and org switching so active org and role context are explicit.
3. Refactor frontend authenticated entry to consume one canonical bootstrap outcome.
4. Gate shell and dashboard readiness on resolved bootstrap state.
5. Remove duplicated manual token and onboarding logic that conflicts with the canonical flow.
6. Add regression tests for each targeted failure mode before treating the hardening as complete.

Rollback strategy:

- Because this change preserves existing architecture, rollback should be limited to reverting the hardening patch set if a critical regression appears.
- Contract changes should stay backward-compatible during implementation where feasible so frontend and backend updates can land safely together.

## Open Questions

- Whether the current login response already contains enough active-org and role information, or whether a normalized response body will need to be expanded
- Which frontend service should own the canonical bootstrap result without introducing a second session system
- Whether some permission hydration can be derived from the same authoritative org-context response to reduce extra round trips
