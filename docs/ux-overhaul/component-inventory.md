# Component Inventory

Evidence: `frontend/src/app/components`, `frontend/src/app/shared`, Storybook stories.

## Shared Shell Components

| Component | Path | Current purpose | Redesign decision |
| --- | --- | --- | --- |
| `HomeComponent` | `pages/home` | Authenticated shell, sidebar/header, lesson mode. | Keep as base shell but introduce role-aware shell metadata. |
| `SidebarComponent` | `components/echo-sidebar` | Workspace nav filtered by permissions. | Replace one-size nav with role-specific nav sections using same permission service. |
| `EchoHeaderComponent` | `components/echo-header` | Brand, breadcrumbs, org switcher, profile menu. | Keep org switch contract; redesign as role-aware app bar. |
| `EchoBreadcrumbsComponent` | `components/echo-breadcrumbs` | URL-derived breadcrumbs. | Keep, but add custom labels and hierarchy map. |
| `IconModule/AppIconComponent` | `shared/icon` | Inline SVG icon set. | Extend icon set and document size/label rules. |

## Foundational UI Components

| Component | Path | Storybook | Current maturity | Redesign decision |
| --- | --- | --- | --- | --- |
| Button | `components/echo-button` | Yes | Basic | Standardize variants, sizes, icon support, loading state. |
| Input | `components/echo-input` | Yes | Basic | Add label/hint/error API. |
| Select | `components/echo-select` | Yes | Basic | Add described-by and validation states. |
| Textarea | `components/echo-textarea` | Yes | Basic | Align with input. |
| Checkbox | `components/echo-checkbox` | Yes | Basic | Add group semantics guidance. |
| Radio | `components/echo-radio`, `echo-radio-group` | Yes | Basic | Ensure keyboard arrow behavior. |
| Toggle | `components/echo-toggle` | Yes | Basic | Use switch semantics. |
| Modal | `components/echo-modal` | Yes | Basic confirmation | Upgrade to accessible dialog with focus trap and destructive variant. |
| Tooltip | `components/echo-tooltip` | Yes | Basic | Use for icon-only nav/actions. |
| Toast | `components/echo-toast`, `echo-toast-container` | Yes | App feedback | Add severity and persistence rules. |
| Loading state | `components/echo-loading-state` | Yes | Strong | Keep; add skeleton variants. |
| State panel | `components/echo-state-panel` | Yes | Strong | Keep; expand empty/error/permission/success patterns. |
| Badge | `components/echo-badge` | Yes | Basic | Separate status pill vs achievement badge. |
| Stat card | `components/stat-card` | No | Dashboard metric | Replace with metric tile spec. |
| Timeline | `components/timeline` | No | Event timeline | Redesign for learner history/activity audit. |

## Domain Components

| Component | Path | Purpose | Redesign decision |
| --- | --- | --- | --- |
| `StudentCourseCardComponent` | `components/student-course-card` | Student course summary/action. | Promote to course card variants for assigned, available, complete. |
| `LessonViewerComponent` | `shared/lesson-viewer.component` | Renders lesson content and activities. | Keep runtime contract; redesign layout/controls. |
| `StorybookViewerComponent` | `components/storybook-viewer` | Storybook pages/media. | Add image loading/error/public URL guidance. |
| `ColoringCanvasComponent` | `components/coloring-canvas` | Interactive coloring activity. | Audit keyboard/touch accessibility before broad use. |
| `AfricaMapExplorerComponent` | `components/africa-map-explorer` | Map exploration. | Use historical-geographic visual guidance and keyboard fallback. |
| `AchievementItemComponent` | `components/achievement-item` | Learner achievement. | Align with achievement display spec. |
| `DemoTourOverlayComponent` | `components/demo-tour-overlay` | Guided demo overlay. | Keep demo-only; avoid required workflows hidden in tour. |
| `EE design system` | `components/ee-design-system` | Presentational components. | Existing V2 layer should be reconciled with new tokens, not expanded blindly. |

## Page Components

Major page components include public/auth (`landing`, `login`, `registration`, `public-products`), learner (`student-view`, `learner-portal`, `lesson-view`, `programs`, `assessment-detail`, `certifications`), teacher (`teacher-view`, `sections`, `section-detail`), admin (`admin-view`, `admin-users`, `admin-courses`, `admin-badges`), content/workspace (`workspace-dashboard`, `product-studio`, `project-detail`, `product-detail`, `review-center`, `access-grants`, `workspace-analytics`, `v2-collection-page`).

## Component Debt

- Several components use local styling instead of shared tokenized states.
- Storybook coverage is incomplete for domain components and page states.
- Data tables/lists are page-local and should become a shared responsive data component.
- Dialogs need focus management and destructive-action copy standards.
- Icon taxonomy is small and should be intentionally mapped to role navigation.
