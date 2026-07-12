# Shared Component Status

## Added In Phase 1

| Component | Path | Status | Notes |
| --- | --- | --- | --- |
| Shell navigation service | `frontend/src/app/services/shell-navigation.service.ts` | Production active | Centralizes role-to-navigation and canonical route logic using existing permissions. |
| Confirmation dialog | `frontend/src/app/components/echo-confirmation-dialog/` | Available, not broadly connected | Supports default, destructive, and publish variants; focus trap and Escape behavior covered by unit tests. |
| Skeleton | `frontend/src/app/components/echo-skeleton/` | Available | Tokenized primitive for later page migrations. |
| Student curriculum | `frontend/src/app/components/student-curriculum/student-curriculum.component.ts` | Production active for student course overview | Renders unit hierarchy, lesson state labels, locked/current/complete states, and mobile layout. |

## Migrated Or Extended

| Component | Path | Status | Notes |
| --- | --- | --- | --- |
| Button | `frontend/src/app/components/echo-button/echo-button.component.ts` | Extended in Phase 2 | Adds `secondary` color support and optional `ariaLabel` for accessible student action labels. |
| Confirmation dialog | `frontend/src/app/components/echo-confirmation-dialog/` | Connected to assessment submission | Used as a neutral consequential confirmation before assessment attempts. |
| Lesson viewer | `frontend/src/app/shared/lesson-viewer.component.*` | Migrated for local activity states | Adds activity instruction, quiz validation alert, and current step state text without adding scoring behavior. |
| Certifications page | `frontend/src/app/pages/certifications/` | Migrated for student achievements | Uses shared loading, empty, and error states and learner-facing certificate language. |
| Authenticated shell | `frontend/src/app/pages/home/` | Production active | Adds skip link, role-aware mobile navigation, overlay, scroll lock, and focus return. |
| Header | `frontend/src/app/components/echo-header/` | Production active | Uses role-aware shell titles and shared state panels for organization states. |
| Sidebar | `frontend/src/app/components/echo-sidebar/` | Production active | Uses role-aware navigation sections and tokenized active/focus states. |
| State panel | `frontend/src/app/components/echo-state-panel/` | Production active | Adds `permission` and `success` variants and real icon rendering. |
| Access denied | `frontend/src/app/pages/access-denied/` | Migrated | Uses shared permission state. |
| Icon registry | `frontend/src/app/shared/icon/icon.module.ts` | Extended | Adds `Lock` and `CheckCircle` paths. |
| Student curriculum | `frontend/src/app/components/student-curriculum/student-curriculum.component.ts` | Reused in teacher preview | Teacher course preview renders the same unit/lesson hierarchy in preview-only mode without starting learner progress. |
| Confirmation dialog | `frontend/src/app/components/echo-confirmation-dialog/` | Connected to teacher assignment creation | Class assignments require review confirmation before calling the existing section assignment API. |
| State panel/loading state | `frontend/src/app/components/echo-state-panel/`, `frontend/src/app/components/echo-loading-state/` | Connected to Teach routes | Teacher overview, classes, class detail, curriculum, course preview, and learner detail use shared loading/error/empty/permission states. |

## Added In Teacher Phase

| Component/screen | Path | Status | Notes |
| --- | --- | --- | --- |
| Teacher curriculum page | `frontend/src/app/pages/teacher-curriculum/teacher-curriculum.component.ts` | Production active | Course search and preview/assign entry over `/api/courses`. |
| Teacher course preview | `frontend/src/app/pages/teacher-curriculum/teacher-course-preview.component.ts` | Production active | Preview-only course hierarchy over `/api/courses/{id}`. |
| Teacher learner detail | `frontend/src/app/pages/teacher-learner-detail/teacher-learner-detail.component.ts` | Production active | Requires class `sectionId` context and roster verification. |

## Still Legacy

- Form controls, tables, filter controls, page-specific buttons, dashboard cards, and internal page layouts are still mixed Tailwind/SCSS implementations.
- Existing Storybook/design-lab artifacts remain references; production consumers were not migrated wholesale.
- Destructive actions still need page-by-page adoption of `EchoConfirmationDialogComponent`.
- Form controls, tables, filter controls, page-specific buttons, dashboard cards, and internal page layouts are still mixed Tailwind/SCSS implementations.
- Activity controls delegated to canvas, map, and storybook components still need full accessibility and responsive QA.
- Global teacher assignment list is still a class-first alias because no global assignment API was verified.
- Teacher feedback panels remain deferred because no feedback persistence endpoint was verified.

## Required Future Adoption

- Admin user deletes/role changes.
- Course archive/delete/publish actions.
- Badge create/update/delete flows.
- Organization invite revocation.
- Access grant revoke flows.
- Product publish/review transitions.
