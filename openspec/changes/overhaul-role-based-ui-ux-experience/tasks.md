## 1. Design Tokens and Foundations

- [x] 1.1 Review `frontend/src/styles/tokens/*` against `docs/ux-overhaul/design-tokens.md`; affected screens: all; components: all; APIs: none; tests: token lint/build; a11y: contrast pairs documented; responsive: breakpoint tokens verified; frontend-only: yes; rollback: remove token imports.
- [x] 1.2 Introduce token imports behind a low-risk stylesheet layer without replacing production page styles; affected screens: shared shell only; components: shell/header/sidebar; APIs: none; tests: `npm run build`; a11y: focus tokens preserved; responsive: no layout regression; frontend-only: yes; rollback: remove import.
- [x] 1.3 Remove remaining investor/commercial visible copy from public and workspace labels while preserving route compatibility; affected screens: landing, workspace community/access; components: nav/page headers; APIs: none; tests: copy search; a11y: labels remain descriptive; responsive: no clipping; frontend-only: yes; rollback: copy revert.

## 2. Shared Controls and States

- [ ] 2.1 Upgrade shared buttons, icon buttons, links, inputs, selects, textareas, checkboxes, radios, switches, and search controls to the component spec; affected screens: all forms; APIs: none; tests: Karma component specs and Storybook stories; a11y: labels/errors/described-by; responsive: 44px touch targets; frontend-only: yes; rollback: per component.
- [ ] 2.2 Add responsive data-list component for rosters, users, assignments, and review queues; affected screens: teacher class, admin users, review center; APIs: none; tests: component specs; a11y: table/card parity and keyboard actions; responsive: 390px layout; frontend-only: yes; rollback: page-local fallback.
- [x] 2.3 Add shared confirmation dialog with destructive, publish, and revoke variants; affected screens: admin users, admin courses, badges, access grants, product publish; APIs: none; tests: dialog focus/confirm/cancel specs; a11y: focus trap and object naming; responsive: mobile dialog; frontend-only: yes; rollback: disable new wrapper.
- [ ] 2.4 Standardize loading, empty, error, success, and permission denied states; affected screens: all pages with API calls; APIs: none; tests: state component specs and page snapshots; a11y: status/alert semantics; responsive: compact variants; frontend-only: yes; rollback: existing page states.
  - [x] 2.4a Add and demonstrate shared loading, empty, error, success, and permission states in shell/access-denied representative routes.

## 3. Application Shell and Navigation

- [x] 3.1 Implement role-aware nav configuration using existing `PermissionsService`; affected screens: `/home`, `/learn`, `/workspace`; components: shell/sidebar/header/mobile nav; APIs: `/api/orgs` existing; tests: guard/nav Karma specs; a11y: landmarks, labels, focus; responsive: mobile learner nav and staff drawer; frontend-only: yes; rollback: old nav config.
- [x] 3.2 Add role-specific shell titles and contextual page headers; affected screens: all authenticated; components: `HomeComponent`, `EchoHeaderComponent`, breadcrumbs; APIs: none; tests: shell specs; a11y: one page h1 and useful landmarks; responsive: header compaction; frontend-only: yes; rollback: old header copy.
- [x] 3.3 Add default landing routing policy for role spaces while preserving current route paths; affected screens: login/session flow; components/services: auth login, preferences optional; APIs: existing auth/org; tests: login/guard specs; a11y: no impact; responsive: no impact; frontend-only: yes unless preferred landing is persisted; rollback: route to `/home`.

## 4. Authentication and Public Pages

- [ ] 4.1 Redesign landing page around community mission and public learning; affected screens: `/`; components: public header/cards/footer; APIs: none; tests: visual smoke; a11y: heading/contrast/link labels; responsive: 1440/768/390; frontend-only: yes; rollback: old landing component.
- [ ] 4.2 Redesign public products and detail pages; affected screens: `/products`, `/products/:slug`; APIs: `/api/public/products`; tests: service/page specs; a11y: product headings and empty/error states; responsive: card/list layout; frontend-only: yes; rollback: old templates.
- [ ] 4.3 Redesign login, registration, and organization onboarding; affected screens: `/login`, `/registration`, `/onboarding/organization`; APIs: `/api/auth/token`, `/api/auth/register`, `/api/meta/enums`, `/api/orgs`, `/api/orgs/{id}/switch`; tests: existing auth/onboarding specs; a11y: form validation and errors; responsive: no clipped forms; frontend-only: yes; rollback: old templates.

## 5. Student Experience

- [ ] 5.1 Make `/learn` the student-first dashboard using existing learner/student data; affected screens: `/learn`, current student dashboard; APIs: `/api/student-courses`, `/api/analytics/student-progress`, badge/certification/program APIs; tests: student view specs; a11y: next action first; responsive: mobile bottom nav; frontend-only: yes; rollback: current dashboard.
- [ ] 5.2 Redesign learner course library and course overview; affected screens: `/learn/products`, `/home/courses`; APIs: `/api/courses`, `/api/learner-portal/products`, `/api/enroll`; tests: service/page specs; a11y: card labels/status; responsive: filter drawer; frontend-only: yes; rollback: current catalog.
- [ ] 5.3 Redesign lesson player and activity/assessment states without changing governed progress APIs; affected screens: `/learn/lesson/:id`, `/home/lesson/:id`, `/home/assessments/:id`; APIs: progress, lessons, assessments; tests: lesson/assessment specs and Playwright student smoke; a11y: live save/advance announcements; responsive: sticky mobile action bar; frontend-only: yes; rollback: old lesson template.
- [ ] 5.4 Redesign progress, achievements, certifications, and learner resources; affected screens: progress sections, `/learn/certificates`, `/learn/resources`; APIs: analytics, badges, certifications, resources; tests: component/page specs; a11y: no color-only progress; responsive: single-column mobile; frontend-only: yes; rollback: previous sections.

## 6. Teacher Experience

- [ ] 6.1 Redesign teacher Today dashboard around learner support and classes; affected screens: teacher dashboard; APIs: `/api/courses`, `/api/users/students`, `/api/analytics/teacher-summary`, governance summary; tests: teacher specs; a11y: data list summaries; responsive: priority stack; frontend-only: yes; rollback: old teacher view.
- [ ] 6.2 Redesign classes/sections and class detail; affected screens: `/home/sections`, `/home/sections/:id`, cohort aliases; APIs: sections, roster, assignments, section analytics; tests: section specs and Playwright teacher flow; a11y: tabs/list keyboard support; responsive: tabs/cards; frontend-only: yes; rollback: old templates.
- [ ] 6.3 Add guided assignment workflow over existing assignment/assign-course APIs; affected screens: class detail assignment flow; APIs: `/api/sections/{id}/assignments`, `/api/assign-course`; tests: workflow specs; a11y: stepper and validation; responsive: mobile wizard; frontend-only: yes; rollback: current inline assignment controls.
- [ ] 6.4 Redesign curriculum preview, learner progress, review/feedback, and discussion/moderation surfaces where existing APIs support them; affected screens: curriculum, assessment, discussion; APIs: courses, assessments, posts/threads; tests: targeted specs; a11y: form/table semantics; responsive: data cards; frontend-only: yes unless feedback/moderation persistence is selected; rollback: hide unsupported surfaces.

## 7. Administrator Experience

- [ ] 7.1 Redesign admin dashboard with alerts before routine metrics; affected screens: admin dashboard; APIs: `/api/analytics/overview`, users, courses, governance summary; tests: admin specs; a11y: alert ordering; responsive: metrics stack; frontend-only: yes; rollback: old admin view.
- [ ] 7.2 Redesign user and role management with confirmation flows; affected screens: `/home/admin/users`; APIs: `/api/users`, org/invite APIs; tests: user management specs; a11y: data list and confirmation; responsive: filters drawer; frontend-only: yes; rollback: old admin users.
- [ ] 7.3 Redesign course, badge, upload/asset, reporting, moderation, and platform settings surfaces; affected screens: admin courses, badges, analytics/reports, review/moderation; APIs: courses, badges, uploads, analytics, review, posts/threads; tests: page specs; a11y: destructive/publish confirmations; responsive: data list; frontend-only: yes unless asset library/moderation backend is selected; rollback: old surfaces.

## 8. Studio, Organization, and Community Surfaces

- [ ] 8.1 Redesign Studio navigation and product/source/artifact/review screens for content admins; affected screens: workspace projects/product-studio/products/sources/artifacts/review; APIs: V2 platform APIs; tests: V2 service/page specs; a11y: review status text; responsive: queue cards; frontend-only: yes; rollback: old workspace templates.
- [ ] 8.2 Redesign organization people, invites, access, and settings over existing org/invite/access APIs; affected screens: org invites, access grants, settings; APIs: orgs, invites, access grants; tests: org/access specs; a11y: role descriptions and confirmation; responsive: mobile lists; frontend-only: yes; rollback: old screens.
- [x] 8.3 Rename visible community-facing labels while preserving `/workspace/commercial` route until alias/deprecation is planned; affected screens: community route/nav; APIs: none; tests: route/nav specs and copy search; a11y: clear labels; responsive: no layout regression; frontend-only: yes; rollback: label revert.

## 9. Responsive and Accessibility Hardening

- [ ] 9.1 Run keyboard and screen-reader pass on public, auth, student lesson, teacher class detail, and admin user management; affected screens: critical flows; APIs: none; tests: manual QA plus automated a11y where available; a11y: WCAG 2.2 AA checklist; responsive: 390/768/1280/1440; frontend-only: yes; rollback: fix per component.
- [ ] 9.2 Add visual regression screenshots for representative role flows; affected screens: design acceptance set; APIs: seeded demo backend where needed; tests: Playwright screenshots; a11y: focus screenshots where useful; responsive: desktop/mobile; frontend-only: yes; rollback: update/remove snapshots.
- [ ] 9.3 Verify no text clipping, overlap, inaccessible icon-only controls, or color-only status remains; affected screens: all redesigned screens; tests: visual QA checklist; a11y: target size/contrast; responsive: all target widths; frontend-only: yes; rollback: targeted CSS/component fixes.

## 10. Deprecated Styles and Compatibility Cleanup

- [ ] 10.1 Remove deprecated duplicated style utilities only after migrated screens no longer depend on them; affected screens: all migrated; APIs: none; tests: build, Karma, visual; a11y: focus styles preserved; responsive: no regression; frontend-only: yes; rollback: restore styles.
- [x] 10.2 Add route alias/deprecation plan for `/home` and `/workspace/commercial` only after production navigation is stable; affected screens: routing; APIs: none; tests: router specs and smoke tests; a11y: no dead ends; responsive: no impact; frontend-only: yes; rollback: remove redirects.
- [x] 10.3 Update documentation and implementation notes with final backend changes avoided and any future backend proposals; affected docs: `docs/ux-overhaul/*`; APIs: documented only; tests: OpenSpec validation; a11y/responsive: documentation complete; frontend-only: yes; rollback: doc update.
