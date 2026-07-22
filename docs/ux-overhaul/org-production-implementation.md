# Organization Administration Production Implementation

Date: 2026-07-14

## Delivered experience

Phase 6 adds the guarded `/organization` product family for active `org_admin` memberships:

- Overview with defined member, teacher, student, invitation, class, and available-learning counts plus supported attention states.
- Privacy-minimized member, teacher, and student lists with search and role/status filters.
- Invitation creation and status visibility, token omission, and confirmation for privileged organization roles.
- Organization-wide class list and scoped detail with roster and aggregate activity context.
- Read-only course, learning-path, and certification availability without Studio authoring or unsafe access mutation.
- Organization identity and name editing, with unsupported settings clearly separated.

Legacy workspace and Teach routes remain available. Canonical navigation now sends Organization administrators to the new route family and removes Teacher-only items from their Organization navigation.

## Backend changes

No database migration or model lifecycle was added. Two narrow read contracts were added: organization members and organization sections. A shared scoped-section resolver now protects roster, enrollment, assignment, and section-summary endpoints, and enrollment targets must be active members of the same organization.

## Components and reuse

New page components cover overview, people modes, invitations, classes/detail, courses, and settings. They reuse the role-aware shell, `PermissionsService`, semantic tokens, shared state components, shared confirmation dialog, existing organization/V2 services, and responsive record conventions. No separate component system or frontend permission model was introduced.

## Verification

- Backend: all 228 tests passed; 226 passed in the full run and the two upload tests passed after clearing a stale test-temporary-directory ACL.
- Frontend unit suite: 284 tests passed in ChromeHeadless.
- Frontend production build: passed; the current 1.42 MB initial bundle exceeds the 1.25 MB warning budget by 170.89 kB.
- Playwright: all 16 seeded smoke, authorization, accessibility, and visual-regression tests passed in Chromium.
- OpenSpec: strict validation passed with all 33 tasks complete.

## Limitations and deferred work

Member mutations, invite resend/cancel, class editing, member-safe course access changes, organization branding/contact/time-zone settings, advanced reporting, audit logs, announcements, licensing, district hierarchy, and bulk import/export remain unsupported. The backend gap register captures these without presenting nonfunctional controls.
