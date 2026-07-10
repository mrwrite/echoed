# Accessibility Audit

Evidence: `frontend/src/app/components/accessibility-focus.spec.ts`, `echo-header`, `echo-sidebar`, `echo-loading-state`, `echo-state-panel`, `lesson-view`, `assessment-detail`, global `styles.scss`.

## What Works

- Skip link exists in `HomeComponent` and targets `#echoed-main-content`.
- Main content is focusable with `tabindex="-1"`.
- Sidebar collapsed links set accessible labels and titles.
- Header profile menu uses `aria-haspopup`, `aria-expanded`, `role="menu"`, and `role="menuitem"`.
- Loading component specs verify status semantics.
- State panel specs verify alert semantics for errors.
- Global focus styles are tested to ensure focus is not suppressed.
- Lesson and assessment specs include accessible loading/error/unavailable states.

## Risks by Area

| Area | Risk | Severity | Evidence | Recommendation |
| --- | --- | --- | --- | --- |
| Navigation | Collapsed sidebar is icon-only and has no persistent visible text. | High | `echo-sidebar.component.html` | Add tooltips, 44px target minimum, mobile bottom navigation for learners, visible section title in expanded mode. |
| Shell semantics | Header says "Command center" and "Workspace OS" for all roles. | Medium | `echo-header.component.html`, `home.component.html` | Role-specific shell title and landmark labels. |
| Motion | Many page/card animations are globally applied. | Medium | `styles.scss` | Keep reduced-motion token and limit nonessential animation. |
| Contrast | Multiple legacy tokens and translucent backgrounds make contrast hard to guarantee. | High | `styles.scss`, page SCSS | Use semantic token contrast targets and document pairings. |
| Forms | Component APIs vary across native, reactive, and custom controls. | Medium | registration, onboarding, course wizard | Standardize label, hint, error, described-by behavior. |
| Tables | Teacher/admin dense tables may lack complete mobile/screen-reader alternatives. | High | teacher/admin specs and templates | Use responsive data list component with row summary and actions. |
| Confirmation | Deletions can happen without a shared confirmation dialog. | High | admin/teacher dashboard delete handlers | Require confirmation dialog with object name and irreversible-action copy. |
| Lesson runtime | Recovery states exist but screen-reader progression announcements need review. | Medium | `lesson-view.component.ts` | Announce segment completion and next lesson load through live region. |
| Discussion | Posts/threads API exists, but UI coverage is unclear. | Medium | backend `posts.py`, `threads.py` | Design moderated discussion component before exposing broadly. |

## WCAG 2.2 AA Standards for Redesign

- Text contrast at least 4.5:1, large text 3:1.
- Non-text contrast at least 3:1 for controls, focus indicators, icons, chart segments.
- Focus indicator minimum 2 CSS px outline or equivalent contrast area.
- Target size 24px minimum, 44px recommended for primary touch actions.
- Keyboard access for all menus, dialogs, tabs, drawers, comboboxes, lesson controls, quiz controls.
- Error messages programmatically associated with fields.
- Loading states use `role="status"` and do not trap focus.
- Error states use `role="alert"` only when immediate announcement is needed.
- Reduced motion honors `prefers-reduced-motion`.
- No information conveyed only by color.

## Required Accessibility QA

1. Keyboard-only pass for public, auth, student lesson, teacher class detail, admin user management.
2. Screen-reader pass for navigation landmarks, page titles, table/list summaries, lesson completion.
3. Contrast audit of tokens and real screens.
4. Mobile target-size audit at 390px width.
5. Form validation audit across login, registration, onboarding, invites, assignment creation, course wizard.
