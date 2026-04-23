## Why

New users can indicate they want an organization during registration, but the current flow only stores that intent in session state and defers the actual setup until after login. That creates a fragmented first-run experience and increases the risk that users land in the app without clear organization context, while several registration and shell UI surfaces also have readability and layout issues that make onboarding feel unfinished.

## What Changes

- Turn organization setup into an explicit part of first-time registration and onboarding so users can move from account creation to a usable organization context without hidden session-state handoffs.
- Define clear post-registration behavior for users who create an organization, users who skip setup, and users who only have a personal organization.
- Improve registration page readability and contrast for key text, inputs, and helper content.
- Update the authenticated app shell so the sidenav layout behaves predictably across expanded and collapsed states and remains usable on first dashboard paint.

## Capabilities

### New Capabilities
- `registration-organization-setup`: Registration and first-run onboarding capture organization setup intent, preserve the right defaults by role, and guide users into an active non-personal organization when needed.
- `app-shell-accessibility-layout`: Registration and shell surfaces meet clearer contrast expectations and the sidenav layout remains readable, stable, and role-aware in collapsed and expanded states.

### Modified Capabilities

- None.

## Impact

- Affected frontend areas include `frontend/src/app/pages/registration`, `frontend/src/app/pages/login`, onboarding and organization services, and the shared sidebar/home shell components.
- Affected backend/API behavior may include registration and organization creation handoff expectations, depending on whether org setup remains a two-step flow or becomes part of registration completion.
- Test coverage will need updates for registration decisions, onboarding redirects, and sidebar/layout rendering states.
