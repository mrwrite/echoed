# Design Debt Register

| ID | Debt | Severity | Evidence | Impact | Recommended resolution |
| --- | --- | --- | --- | --- | --- |
| DD-01 | One shared sidebar for all creator roles. | High | `echo-sidebar.component.ts` navSections | Users see product/workspace labels unrelated to their task. | Role-specific nav model using same permissions. |
| DD-02 | `/home`, `/learn`, and `/workspace/learners` overlap. | High | `app.routes.ts` | Learner and staff journeys lack a canonical path. | Make `/learn` learner canonical; staff learner management under Teach/Admin. |
| DD-03 | Commercial route/component naming remains. | Medium | `/workspace/commercial`, `CommercialDashboardComponent` | Conflicts with community GitHub project direction. | Rename visible IA to Community; plan route alias/deprecation later. |
| DD-04 | Global styles define multiple visual systems. | High | `styles.scss` | Inconsistent color, radius, shadow, motion, contrast. | Introduce separate token files, then migrate incrementally. |
| DD-05 | Overuse of cards and oversized hero-like page headers in app surfaces. | Medium | `.ee-page-header`, dashboard views | Operational screens become harder to scan. | Adopt dense but warm learning-platform layouts. |
| DD-06 | Destructive actions lack shared confirmation standard. | High | `deleteCourse`, `deleteUser` handlers | Accidental deletion risk. | Shared confirmation dialog with named object and role copy. |
| DD-07 | Parent role is exposed before product support exists. | Medium | registration role options, backend enum | Parent users can register with no destination. | Mark parent as future/limited and route to family setup placeholder only if implemented. |
| DD-08 | Super admin inconsistently surfaced. | Medium | backend V2 creator roles include; frontend route constants omit | Privileged users may hit access-denied. | Align frontend route constants to backend role support after decision. |
| DD-09 | Breadcrumb labels are URL-derived. | Medium | `echo-breadcrumbs.component.ts` | Labels like product-studio and IDs are not user-friendly. | Add route metadata label map and entity title support. |
| DD-10 | Storybook assets use backend-hosted files and need deployed URL discipline. | Medium | `backend/storybook`, prior deployment issue | Broken images in Vercel if localhost leaks. | Asset URL helper contract and visual tests. |
| DD-11 | Dashboard data density is not role-prioritized. | High | student/teacher/admin dashboard components | Key actions compete with secondary metrics. | Dashboard hierarchy by daily tasks and alert priority. |
| DD-12 | Discussion/community UI is not clearly discoverable. | Medium | backend posts/threads APIs | Community mission is underrepresented. | Design moderated discussion hub before full exposure. |
| DD-13 | Form patterns vary across template-driven, reactive, and custom controls. | Medium | login, registration, course wizard, invites | Validation consistency suffers. | Component spec and phased migration. |
| DD-14 | Visual asset/brand source is unclear. | Medium | no logo asset found, only `EE` mark | Hard to preserve brand concept. | Locate/import brand asset before production visual replacement. |
| DD-15 | Implementation placeholder copy leaks into UX. | Medium | V2 collection route data says "Read-only", "later phase" | Users see roadmap instead of task guidance. | Convert to user-centered empty and unavailable states. |
