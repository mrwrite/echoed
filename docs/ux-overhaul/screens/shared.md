# Shared Screen Specifications

## Application Shell

- Role: all authenticated roles.
- Goal: provide correct navigation and org/user context.
- API: session token, `/api/orgs`, preferences.
- States: session loading, org loading, org switch pending/error/success, permission denied.
- Accessibility: skip link, landmarks, visible focus, keyboard profile menu.
- Backend changes: none.

## Empty State

- Components: `EchoStatePanelComponent` target.
- Required fields: eyebrow optional, title, explanation, primary action, secondary action optional.
- Variants: learner no assignments, teacher no classes, admin no results, studio no artifacts.

## Loading State

- Components: `EchoLoadingStateComponent`, skeleton variants.
- Behavior: preserve page structure where known; use status semantics.

## Error State

- Required: what failed, impact, retry action, support path if persistent.
- No raw backend traces.

## Permission Denied

- Required: current role/org context, missing access explanation, profile/org switch action, back action.

## Search and Filter

- Shared across public product catalog, curriculum library, rosters, users, review queues.
- Mobile filters use drawer or stacked chips.

## Notifications

- Proposed, not currently fully implemented.
- Types: assignment, feedback, content review, access/invite, discussion moderation, system.
- Backend changes: required only when real persistent notifications are implemented.

## Profile and Preferences

- Route/component: `PreferencesComponent`.
- Requirements: display name, preferences, accessibility settings, preferred role/space if multi-role.
- Backend changes: optional preference fields for preferred landing space.
