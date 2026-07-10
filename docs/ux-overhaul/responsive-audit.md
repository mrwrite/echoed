# Responsive Audit

Evidence: `HomeComponent.syncShellViewport()`, `home.component.scss`, `echo-sidebar`, page SCSS, tests in `home.component.spec.ts`, teacher/admin responsive specs.

## Current Behavior

- Sidebar collapses automatically below 1024px.
- Compact expanded sidebar acts as an overlay.
- Lesson mode hides header/sidebar and uses a dedicated content surface.
- Many `.ee-grid` patterns use `auto-fit` and `minmax`.
- Several specs verify compact shell width and responsive fallback markup.

## Main Issues

| Issue | Severity | Evidence | Recommended redesign |
| --- | --- | --- | --- |
| Desktop sidebar model dominates all roles. | High | Shared `HomeComponent` shell for `/home`, `/workspace`, `/learn`. | Role-specific desktop nav and learner mobile bottom nav. |
| Teacher/admin tables need consistent card/list fallbacks. | High | Teacher/admin specs mention responsive fallback markup, but no shared data-list spec. | Create responsive data list component. |
| Header org switcher hides on smaller widths. | Medium | `echo-header.component.html` uses `hidden lg:flex`. | Provide compact org/context switcher in profile drawer. |
| Deep routes need breadcrumbs/back behavior on mobile. | High | Breadcrumbs exist in header, hidden hierarchy in lesson mode. | Page header includes contextual back link and breadcrumb on non-lesson deep routes. |
| Touch targets vary by page-local styles. | Medium | Many custom SCSS files. | Tokenize control height: 40 desktop, 44 touch. |
| Dashboards overuse cards and grids. | Medium | Student/teacher/admin views. | Mobile task stack: next action, status, alerts, then secondary content. |

## Breakpoint Strategy

| Breakpoint | Width | Behavior |
| --- | --- | --- |
| Mobile | 390px target, 360px minimum | Single column, bottom nav for learners, top app bar, drawers for filters/secondary nav. |
| Tablet | 768px | Two-column where content allows, collapsible rail for staff, persistent page actions. |
| Small desktop | 1280px | Staff sidebar plus content max width, secondary nav tabs. |
| Desktop | 1440px | Full role nav, contextual panels, readable data density. |

## Screen-Specific Responsive Priorities

- Landing/login/registration: first viewport must show brand, action, and no clipped form fields.
- Student dashboard: next lesson remains first; achievements/progress below.
- Lesson player: content and activity controls remain in one column on mobile, with sticky safe exit.
- Teacher dashboard: class priorities and learner support before governance detail.
- Class detail: roster and assignments become tabs on mobile.
- Admin users: filters collapse into drawer; table becomes data list.
- Studio/review: queue filters become horizontal chips or drawer.
