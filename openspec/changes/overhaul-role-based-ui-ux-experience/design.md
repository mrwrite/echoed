## Context

EchoEd currently has a mature backend domain model and APIs for authentication, organizations, curriculum, lessons, progress, assignments, sections, analytics, V2 content operations, uploads, badges, and discussion primitives. The frontend has three overlapping route families: `/home`, `/workspace`, and `/learn`. The same shared shell currently presents generic "Workspace OS" language across roles, while route guards and services already contain enough role information to present role-specific navigation.

The UX audit and design artifacts for this change live under `docs/ux-overhaul/`, the Figma-ready package under `design/figma/`, and isolated coded reference screens under `frontend/design-lab/`.

## Goals / Non-Goals

**Goals:**

- Implement the overhaul incrementally from foundations to shared components, then role-specific screens.
- Preserve existing backend auth, organization, role, permission, curriculum, progress, lesson, assignment, section, review, upload, analytics, and discussion contracts unless a separate proposal justifies a backend change.
- Make `/learn` the canonical learner mental model, while keeping compatibility with current routes during migration.
- Introduce role-aware shell/navigation for students, teachers/instructors, content admins, org admins, admins, and super admins where supported.
- Standardize loading, empty, error, permission, confirmation, responsive data, and accessibility behavior.
- Replace investor/commercial wording with community, stewardship, access, and learning language.
- Add visual regression and accessibility coverage before replacing broad production surfaces.

**Non-Goals:**

- No database schema changes in this change.
- No parallel auth, onboarding, role, permission, course, lesson, progress, assignment, section, organization, discussion, upload, or analytics systems.
- No native Figma file creation unless a Figma connector is introduced later.
- No dark mode implementation in the first production pass.
- No production route deletion until compatibility redirects and tests are in place.

## Decisions

### Decision: Frontend-first IA over existing routes

Use role-specific navigation labels and landing behavior over current routes before adding new physical route aliases.

Rationale: current APIs and guards already support role checks; changing route paths first would add migration risk without improving backend capability.

Alternative considered: replace `/home`, `/workspace`, and `/learn` immediately. Rejected because it risks breaking seeded demos, tests, and deployed links.

### Decision: Keep design tokens separate before migration

Add token files under `frontend/src/styles/tokens` and do not import them into production styles until implementation begins.

Rationale: design phase must not replace active styles. Separate tokens can be reviewed and tested before migration.

Alternative considered: directly rewrite `styles.scss`. Rejected because the repository currently has overlapping style systems and broad replacement would be high-risk.

### Decision: Role-aware shell uses `PermissionsService`

The shell and nav must consume canonical roles/permissions resolved by `PermissionsService`, not raw token reads or duplicate role logic.

Rationale: `PermissionsService` already combines JWT role, active organization role, org hydration, onboarding state, and permission mapping.

Alternative considered: define a new frontend role resolver. Rejected because it would duplicate auth/org session behavior.

### Decision: Responsive data list as shared pattern

Dense teacher/admin tables should use a shared table-to-card responsive pattern rather than page-specific mobile fallbacks.

Rationale: rosters, users, assignments, reports, and review queues share the same accessibility and responsive problems.

Alternative considered: keep page-specific tables. Rejected because it perpetuates inconsistent keyboard and mobile behavior.

### Decision: Coded reference stays isolated

Use `frontend/design-lab` for static reference screens during design phase.

Rationale: Storybook exists but is not currently a complete product-level design lab; static reference is lower risk and does not affect production routing.

Alternative considered: add a development Angular design-lab route immediately. Rejected for design phase to avoid production route churn.

## Risks / Trade-offs

- Route aliases may temporarily coexist with older route families -> mitigate with route inventory, compatibility redirects, and explicit deprecation notes.
- Multi-role users may still need a role switcher -> mitigate with preferred landing preference and clear role cards.
- Parent/viewer roles are partial -> mitigate by documenting them as partial and not exposing unsupported dashboards.
- Existing global styles may conflict with new tokens -> mitigate by migrating one component group at a time with visual tests.
- Static design-lab does not prove Angular behavior -> mitigate with implementation tasks for Storybook/Karma/Playwright coverage.
- Backend gaps may appear during implementation -> mitigate by requiring each backend change to be listed as required or optional before coding.

## Migration Plan

1. Land tokens and foundations without importing into production.
2. Update shared controls and state components.
3. Introduce role-aware shell/navigation using existing `PermissionsService`.
4. Redesign public/auth pages.
5. Redesign student Learn surfaces and lesson player.
6. Redesign teacher classes, assignment, learner support, and reporting surfaces.
7. Redesign admin user/course/badge/reporting and destructive confirmation flows.
8. Redesign Studio/content/community surfaces.
9. Add responsive, accessibility, and visual regression coverage.
10. Deprecate old labels/routes only after compatibility redirects and tests pass.

Rollback: each phase should be mergeable independently. If a phase causes regressions, revert the affected frontend components/routes/styles without backend migration rollback.

## Open Questions

- Should super admin use Admin IA, internal Ops IA, or both?
- Will parent/guardian support be implemented in this overhaul or deferred behind a future Family Portal proposal?
- Is a standalone EchoEd logo asset available outside the repository, and should it replace the current "EE" text mark?
- Which discussion/moderation capabilities are ready to expose in production UI?
