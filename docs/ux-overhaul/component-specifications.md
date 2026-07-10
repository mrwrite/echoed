# Component Specifications

This file defines implementation targets. Production components should migrate incrementally.

## Application Shell

- Purpose: authenticated layout with role-aware navigation, org context, notifications, profile, skip link.
- Variants: student, teacher, studio, organization, admin, lesson.
- States: loading session, org load error, access denied, compact/mobile, multi-role.
- Accessibility: landmarks, skip link, keyboard nav, focus restoration after route changes.
- Responsive: desktop sidebar for staff; learner bottom nav on mobile; lesson hides global chrome.
- Anti-patterns: one generic "Workspace OS" shell for all users.

## Header

- Purpose: page context, org switcher, search, notifications, profile.
- Variants: standard, compact, lesson.
- States: org loading, switch pending/success/error, menu open.
- Keyboard: menu opens with Enter/Space, closes with Escape, arrow navigation optional.

## Sidebar / Primary Navigation

- Purpose: role-specific primary navigation.
- Variants: expanded, collapsed, mobile drawer.
- States: active, hover, focus, disabled/unavailable, loading permissions.
- Accessibility: text label always available; icon-only requires tooltip and `aria-label`.
- Anti-patterns: hiding essential workflows in overflow; unlabeled icons.

## Mobile Navigation

- Purpose: fast access to primary learner/staff tasks.
- Variants: learner bottom nav, staff drawer.
- Accessibility: 44px targets, active state text and icon.

## Breadcrumbs

- Purpose: show hierarchy on deep routes.
- Variants: text, compact back-link.
- Behavior: use route metadata/entity titles, not raw IDs.

## Page Header

- Purpose: title, description, primary action, status.
- Variants: standard, compact, data-heavy, lesson.
- Anti-patterns: hero-scale type in dashboards.

## Tabs

- Purpose: contextual secondary navigation.
- Variants: underline, segmented, scrollable mobile.
- Keyboard: arrow keys move focus; Home/End optional.

## Buttons and Icon Buttons

- Variants: primary, secondary, tertiary, danger, ghost, link; icon-only.
- Sizes: sm 36px, md 44px, lg 48px.
- States: default, hover, active, focus, disabled, loading.
- Accessibility: icon-only needs accessible name and tooltip.

## Form Controls

Controls: inputs, selects, comboboxes, search, checkboxes, radios, switches, textarea, date controls, file upload.

- Required states: default, focus, error, success, disabled, loading.
- Validation: label, hint, error, described-by ID.
- Keyboard: native behavior where possible; combobox follows ARIA practices.
- Anti-patterns: placeholder as label; color-only errors.

## Cards

- Purpose: repeated items and genuinely framed tools.
- Variants: course, lesson, assignment, metric, achievement, empty/action.
- States: active, selected, completed, locked, unavailable.
- Anti-patterns: cards nested inside cards; page sections as floating cards.

## Progress Indicators

- Variants: linear, ring, stepper, status timeline.
- Accessibility: include text value and state.
- Usage: learning progress, assignment completion, publish readiness.

## Badges and Achievements

- Status pill: small operational state.
- Achievement badge: learner accomplishment with image/icon, criteria, date.
- Accessibility: do not rely on color/shape alone.

## Tables and Responsive Data Lists

- Purpose: rosters, users, assignments, reports.
- Desktop: sortable table where useful.
- Mobile: data cards with row title, key facts, actions.
- Accessibility: table headers, captions, filter descriptions, keyboard actions.

## Pagination, Filters, Search

- Filters: chips for common filters, drawer for advanced filters on mobile.
- Search: clear button, results count, empty state.
- Pagination: page size and total count where backend supports it; otherwise document client-side limits.

## Empty, Loading, Error, Permission States

- Empty: explain why empty and next action.
- Loading: skeleton for known layouts, status text for unknown.
- Error: what failed, impact, retry action.
- Permission denied: who can help, current role/org context.

## Overlays

Components: alerts, toasts, banners, tooltips, popovers, menus, dialogs, confirmation dialogs, drawers.

- Dialogs require focus trap, Escape close unless destructive confirmation in progress, labelled title, described body.
- Destructive confirmation must name the object and impact.
- Toasts must not be the only record of critical state changes.

## Domain Components

| Component | Variants | Required behavior |
| --- | --- | --- |
| Course card | Assigned, available, completed, staff preview | Show status, next action, progress, age/grade metadata. |
| Lesson card | Ready, locked, completed, review, enrichment | Explain availability and action. |
| Assignment card | Not started, in progress, submitted, returned, overdue | Due date, target, status, feedback entry. |
| Activity timeline | Student progress, project review, admin audit | Chronological, accessible, filterable. |
| Discussion thread | Learner, teacher, moderator | Moderation state, reply, flag, source/context. |
| Rich content | Lesson body, historical source, source note | Captions, provenance, readable width. |
| Quiz controls | MCQ, short answer, reflection | Submit pending, validation, feedback. |
| Teacher feedback | Inline, rubric, summary | Student-safe feedback language. |
| Charts | Progress, mastery, access, review queue | Text summaries and no color-only legends. |
