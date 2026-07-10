## Why

EchoEd has grown into a multi-role community education platform, but the current frontend still exposes overlapping `/home`, `/learn`, and `/workspace` experiences with generic workspace language, mixed role priorities, and inconsistent visual/component patterns. The product needs a role-based UX overhaul that makes student, teacher, content, organization, and admin workflows clear while preserving existing backend contracts.

## What Changes

- Introduce a role-aware information architecture for Learn, Teach, Studio, Organization, Admin, and Community spaces.
- Add a frontend-first design foundation using new EchoEd design tokens, accessibility standards, and reusable component specifications.
- Redesign public, authentication, student, teacher, administrator, content/studio, organization, and shared state screens around existing APIs.
- Replace investor/commercial-facing language with community project, stewardship, access, and learning language.
- Create an incremental implementation plan that preserves the current JWT auth, organization, curriculum, progress, assignment, section, review, upload, discussion, and analytics systems.
- Add isolated design-lab/reference screens and visual acceptance criteria before production page replacement.
- Require explicit confirmation, accessibility, responsive behavior, and visual regression coverage for high-risk UI changes.

No breaking backend API or database changes are planned for the initial implementation.

## Capabilities

### New Capabilities

- `role-based-ui-ux-experience`: Defines the role-aware frontend UX, navigation, design-system, screen-state, accessibility, responsive, and validation requirements for the EchoEd overhaul.

### Modified Capabilities

- None. Existing auth, organization, curriculum, progress, lesson, assignment, section, review, upload, analytics, and discussion capabilities are reused rather than redefined in this change.

## Impact

- Frontend: Angular routes, shell, sidebar/header, public/auth pages, student learner experience, teacher/class workflows, admin management screens, V2 workspace/studio surfaces, shared UI components, SCSS/Tailwind token usage, Storybook/design-lab references, Playwright/Karma coverage.
- Documentation: UX audit, route inventory, role matrix, API/UI contract map, IA, screen specs, Figma-ready package, usability plan, design QA checklist.
- Backend: no required schema, auth, permission, or route changes for the initial overhaul. Optional backend improvements are documented separately and must be proposed before implementation if selected.
- Tests: Karma/Jasmine for shared components and route behavior, Playwright visual and role-flow smoke tests, accessibility checks, and targeted backend tests only if future API behavior changes.
