## Context

The current registration flow already collects a role and optional organization name, but it does not create or schedule organization setup in a way that is visible and dependable to the user. Registration stores `pending_org_creation` in session storage, login and the home guard both infer whether onboarding is required, and the organization onboarding screen completes creation after authentication. This gives the project a workable foundation, but the responsibility for first-run organization setup is split across registration, login, guard, onboarding, permissions bootstrap, and shell rendering.

The UI issues are similarly cross-cutting. Registration includes low-contrast helper copy and state messaging on a dark gradient surface, while the authenticated shell depends on early session bootstrap so the sidebar can render the correct navigation on first paint. The sidebar also uses fixed positioning and width-based layout offsets, which makes expanded and collapsed behavior sensitive to route timing, viewport width, and initial render state.

## Goals / Non-Goals

**Goals:**
- Make organization setup an explicit and reliable first-run path for newly registered users without introducing hidden state transitions.
- Preserve the current separation between account creation and authenticated organization creation so existing auth/backend contracts stay intact.
- Ensure users who only have a personal org, no orgs, or a pending org setup intent are consistently routed into organization onboarding before normal app use.
- Improve contrast and layout behavior on registration and authenticated shell surfaces so primary actions, helper copy, and navigation remain readable and stable.

**Non-Goals:**
- Redesign the entire authentication stack or replace the existing onboarding route.
- Introduce invite acceptance, membership provisioning, or organization switching changes beyond what is needed for first-run setup.
- Rebuild the full visual system; this change is limited to the affected registration and shell surfaces.

## Decisions

Keep organization creation as an authenticated onboarding step, but tighten the contract between registration, login, guard, and onboarding. Registration will capture whether the user wants to create an organization now, store normalized onboarding intent only when needed, and present clearer copy about what happens next. Login and the home session guard will continue to treat pending setup, zero organizations, and personal-only memberships as onboarding-required states. This preserves the existing backend API shape and avoids adding unauthenticated organization-creation behavior.

Make onboarding the single completion point for first-run org creation. The onboarding page should hydrate from any saved registration intent, allow users to confirm or edit the organization name and inferred type, and, after creation, refresh organizations, switch the active org, refresh permissions, and clear the pending setup token. This gives the shell one clear source of truth for when a user is ready to land in `/home`.

Treat contrast and sidenav issues as app-shell requirements rather than one-off styling tweaks. Registration surfaces should use token-driven text and field styling that meets the app's readable-on-dark and readable-on-light expectations for headings, helper text, warnings, and disabled states. The sidebar and home shell should maintain a predictable content offset and viewport behavior in both collapsed and expanded states, with initial render aligned to the resolved session and visible nav sections.

Alternative considered: create the organization directly during registration. This would reduce one step for some users, but it would require changing unauthenticated registration behavior, handling auth/org rollback more carefully, and aligning backend ownership semantics during account creation. Given the existing onboarding route and current API surface, strengthening the existing two-step flow is the lower-risk option.

## Shared Onboarding Decision

The onboarding-required decision must live in one shared frontend utility, service, or guard-consumable helper and be reused by:
- login post-auth redirect handling
- the home session guard
- any first-run bootstrap flow that determines whether `/home` is allowed

Do not duplicate this decision logic across multiple components, pages, or guards.

## Risks / Trade-offs

- [Session storage remains part of the onboarding handoff] -> Mitigation: keep the payload minimal, normalized, and cleared immediately after successful org creation or explicit opt-out.
- [Login and guard can drift if onboarding rules are duplicated] -> Mitigation: centralize or share the onboarding-required decision so both entry points evaluate the same conditions.
- [Contrast fixes can regress the current visual style] -> Mitigation: prefer design-token or utility updates scoped to registration and shell surfaces, and verify against existing page themes.
- [Sidebar layout adjustments can affect dashboard pages that assume current margins] -> Mitigation: define shell layout behavior at the home container level and validate collapsed, expanded, and lesson-mode states.

## Repo Constraints

Frontend code lives under `frontend/src`.
Backend code lives under `backend/app`.

Existing backend routes already include:
- `backend/app/api/routes/auth.py`
- `backend/app/api/routes/orgs.py`
- `backend/app/api/routes/users.py`
- `backend/app/api/routes/progress.py`
- `backend/app/api/routes/start_course.py`
- `backend/app/api/routes/lesson_sessions.py`

Existing backend core files already include:
- `backend/app/auth.py`
- `backend/app/models.py`
- `backend/app/schemas.py`
- `backend/app/enum.py`

Do not create duplicate routers, duplicate auth flows, duplicate organization setup APIs, or duplicate progress/bootstrap logic.