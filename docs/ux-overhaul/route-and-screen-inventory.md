# Route and Screen Inventory

Evidence: `frontend/src/app/app.routes.ts`, guards in `frontend/src/app/guards`, services in `frontend/src/app/services`, backend route modules in `backend/app/api/routes`.

## Public Routes

| Route | Component | Role access | User goal | Main API dependencies | UX problems |
| --- | --- | --- | --- | --- | --- |
| `/` | `LandingComponent` | Public | Understand EchoEd and enter auth/product discovery | None direct | Must reflect community project, not investor positioning. |
| `/products` | `PublicProductsComponent` | Public | Browse published products | `V2PlatformService.getPublicProducts()` -> `/api/public/products` | Product/course terminology competes with course catalog. |
| `/products/:slug` | `PublicProductDetailComponent` | Public | Inspect public product | `/api/public/products/{slug}` | Needs clear conversion to login/register or learner access. |
| `/login` | `LoginComponent` | Public | Sign in | `/api/auth/token`, `/api/orgs` through bootstrap | Error handling exists; destination can be role-confusing. |
| `/registration` | `RegistrationComponent` | Public | Create account and optional org setup | `/api/auth/register`, `/api/meta/enums` | Supports parent/instructor but lacks role-specific expectations. |
| `/onboarding/organization` | `OnboardingOrganizationComponent` | Authenticated onboarding | Create org after registration | `/api/orgs`, `/api/orgs/{id}/switch` | Required when org context missing; needs clearer role-specific copy. |
| `/access-denied` | `AccessDeniedComponent` | Public/auth | Recover from permission failure | None direct | Needs useful next action by role. |
| `**` | Redirect | Public | Recover from unknown route | None | Redirects to landing instead of contextual 404. |

## Authenticated Shell Routes

| Route family | Component shell | Guard | Notes |
| --- | --- | --- | --- |
| `/home/**` | `HomeComponent` | `HomeSessionGuard`; child `RoleGuard` where needed | Legacy role dashboard and curriculum routes. |
| `/workspace/**` | `HomeComponent` | `HomeSessionGuard` + creator role guards | V2 content/product/community workspace. |
| `/learn/**` | `HomeComponent` | `HomeSessionGuard` | Learner portal route family. |

## `/home` Routes

| Route | Component | Role access | User goal | API dependencies | UX problems |
| --- | --- | --- | --- | --- | --- |
| `/home` | `UserDashboardComponent` + `EchoedRoleSelectorComponent` | Authenticated | Select/resolve role dashboard | Session/org bootstrap | Role selector can become an unnecessary landing step. |
| `/home/courses` | `AvailableCoursesComponent` | Authenticated | Browse courses | `/api/courses`, `/api/enroll` | Mixes learner catalog with staff course concepts. |
| `/home/courses/new` | `CourseWizardComponent` | admin, teacher | Create course | `/api/courses`, `/api/upload/*`, course version routes | Should move to Teach/Admin or Studio IA. |
| `/home/courses/:courseId/edit` | `CourseWizardComponent` | admin, teacher | Edit course | `/api/courses/{id}` | Needs safe-publish/version state in page header. |
| `/home/programs` | `ProgramsComponent` | Authenticated | View/enroll pathways | `/api/programs`, `/api/programs/{id}/enroll` | Role behavior varies but route is shared. |
| `/home/assessments/:id` | `AssessmentDetailComponent` | Authenticated, submit student | Complete assessment | `/api/assessments/{id}`, attempts | Needs role-aware preview vs student submission mode. |
| `/home/certifications` | `CertificationsComponent` | Authenticated | View certifications | `/api/certifications`, `/api/students/me/certifications` | Needs clear student vs staff distinction. |
| `/home/org/invites` | `OrgInvitesComponent` | org_admin, content_admin | Invite org members | `/api/orgs/{orgId}/invites`, `/api/invites/accept` | Needs role descriptions and invite status handling. |
| `/home/studio/courses` | `StudioCoursesComponent` | content_admin, org_admin | Manage course versions | `/api/courses/authoring`, versions | Overlaps `/workspace/product-studio/courses`. |
| `/home/sections` | `SectionsComponent` | teacher, org_admin, instructor | Manage classes | `/api/sections` | Label should be "Classes" for K-5 teachers, "Sections" as secondary. |
| `/home/sections/:id` | `SectionDetailComponent` | teacher, org_admin, instructor | Manage roster/assignments | `/api/sections/{id}/roster`, `/api/sections/{id}/assignments` | Needs clearer assignment workflow. |
| `/home/me/preferences` | `PreferencesComponent` | Authenticated | Manage profile/preferences | `/api/me/preferences` | Should be reachable from all shells with consistent route. |
| `/home/admin/courses` | `AdminCoursesComponent` | admin | Manage courses | `/api/courses` | Overlaps staff and Studio course surfaces. |
| `/home/admin/badges` | `AdminBadgesComponent` | admin | Manage badges | `/api/badges`, `/api/upload/badge` | Needs asset guidance and destructive confirmation. |
| `/home/admin/users` | `AdminUsersComponent` | admin | Manage users | `/api/users`, `/api/users/{id}` | Needs filters, role management, confirmation. |
| `/home/lesson/:id` | `LessonViewComponent` | Authenticated | View governed lesson | `/api/progress/segment`, `/api/lessons/{id}`, `/api/progress/segment/complete` | Shared with learner flow; exit destination should match entry shell. |

## `/workspace` Routes

| Route | Component | Role access | User goal | API dependencies | UX problems |
| --- | --- | --- | --- | --- | --- |
| `/workspace` | `WorkspaceDashboardComponent` | admin, teacher, content_admin, org_admin, instructor | Orient to workspace operations | V2 analytics and workspace APIs | Too broad for every creator role. |
| `/workspace/projects` | `V2CollectionPageComponent` | creator roles | View project shells | `/api/projects` | Empty/read-only language is implementation-first. |
| `/workspace/projects/:projectId` | `ProjectDetailComponent` | creator roles | Inspect project pipeline | `/api/projects/{id}`, project collections | Needs task tabs and breadcrumbs. |
| `/workspace/product-studio` | `ProductStudioComponent` | creator roles | Create project/product/source/artifact shells | `/api/projects`, `/api/products`, `/api/knowledge-sources`, `/api/artifacts` | Many operations in one large form surface. |
| `/workspace/product-studio/create` | `ProductStudioComponent` | creator roles | Create product | Same as above | Duplicate destination. |
| `/workspace/product-studio/generation-runs` | `V2CollectionPageComponent` | creator roles | View generation attempts | `/api/generation-runs` | Read-only placeholder needs clearer future-state framing. |
| `/workspace/product-studio/generation-runs/:generationRunId` | `GenerationRunDetailComponent` | creator roles | Inspect generation run | `/api/generation-runs/{id}` | Needs logs/status structure. |
| `/workspace/product-studio/courses` | `StudioCoursesComponent` | content_admin, org_admin | Author course versions | `/api/courses/authoring`, versions | Duplicates `/home/studio/courses`. |
| `/workspace/product-studio/courses/new` | `CourseWizardComponent` | admin, teacher | Create course | `/api/courses` | Role mismatch with studioRoles. |
| `/workspace/product-studio/courses/:courseId/edit` | `CourseWizardComponent` | admin, teacher | Edit course | `/api/courses/{id}` | Needs consistent course authoring role model. |
| `/workspace/products` | `V2CollectionPageComponent` | creator roles | Manage products | `/api/products` | Product vs course relationship needs explicit labels. |
| `/workspace/products/:productId` | `ProductDetailComponent` | creator roles | Inspect/publish product | `/api/products/{id}`, publish/review/status | Good candidate for contextual secondary nav. |
| `/workspace/products/manage` | `AdminCoursesComponent` | admin | Manage courses | `/api/courses` | Route order may conflict with `products/:productId`; should be reviewed. |
| `/workspace/knowledge-sources` | `V2CollectionPageComponent` | creator roles | Manage sources | `/api/knowledge-sources` | Source ingestion not fully implemented. |
| `/workspace/artifacts` | `V2CollectionPageComponent` | creator roles | Manage artifacts | `/api/artifacts` | Needs artifact type filters. |
| `/workspace/artifacts/:artifactId` | `ArtifactDetailComponent` | creator roles | Inspect artifact | `/api/artifacts/{id}` | Needs review and source provenance layout. |
| `/workspace/review-center` | `ReviewCenterComponent` | creator roles | Review products/artifacts | `/api/review-center`, review-status patches | Good domain but nav label should be visible to content roles first. |
| `/workspace/access` | `AccessGrantsComponent` | creator roles | Manage learner access | `/api/access-grants` | Must avoid marketplace/commercial framing. |
| `/workspace/learners` | `UserDashboardComponent` | creator roles | Open learner management hub | Mixed `/home` child components | Reuses learner dashboard shell inside workspace; IA drift. |
| `/workspace/learners/products` | `AvailableCoursesComponent` | creator roles | View products/courses | `/api/courses` | Learner label with staff permissions is confusing. |
| `/workspace/learners/paths` | `ProgramsComponent` | creator roles | View paths | `/api/programs` | Needs staff vs learner mode. |
| `/workspace/learners/certificates` | `CertificationsComponent` | creator roles | View certificates | `/api/certifications` | Needs reporting view. |
| `/workspace/learners/users` | `AdminUsersComponent` | admin | Manage users | `/api/users` | Duplicates admin users. |
| `/workspace/learners/cohorts` | `SectionsComponent` | teacher, org_admin, instructor | Manage cohorts/classes | `/api/sections` | Label mismatch with sections. |
| `/workspace/learners/cohorts/:id` | `SectionDetailComponent` | teacher, org_admin, instructor | Manage cohort detail | `/api/sections/{id}/roster`, assignments | Should be primary Teacher IA. |
| `/workspace/analytics` | `WorkspaceAnalyticsComponent` | creator roles | View workspace analytics | `/api/analytics/workspace`, products, learners, knowledge-pipeline | Needs role-specific summaries. |
| `/workspace/commercial` | `CommercialDashboardComponent` | creator roles | Community/operations | likely V2 platform data | Component/route retains commercial wording. |
| `/workspace/demo-readiness` | `DemoReadinessComponent` | creator roles | Demo guide | Demo data APIs | Internal readiness route should be dev/demo only. |
| `/workspace/settings` | `PreferencesComponent` | creator roles | Settings | `/api/me/preferences` | Needs org settings separation. |
| `/workspace/settings/invites` | `OrgInvitesComponent` | org_admin, content_admin | Invite members | invites APIs | Should be under Admin/Org. |
| `/workspace/settings/badges` | `AdminBadgesComponent` | admin | Manage badges | badge APIs | Admin only but nested in workspace settings. |
| `/workspace/lesson/:id` | `LessonViewComponent` | Authenticated | Staff lesson preview | lesson/progress APIs | Preview and governed learner delivery should be explicit modes. |

## `/learn` Routes

| Route | Component | Role access | User goal | API dependencies | UX problems |
| --- | --- | --- | --- | --- | --- |
| `/learn` | `LearnerPortalComponent` | Authenticated | Resume learner journey | `/api/learner-portal/products`, progress APIs | Best candidate for student default. |
| `/learn/products` | `LearnerProductsComponent` | Authenticated | Browse available learner products | `/api/learner-portal/products` | Needs assigned vs available split. |
| `/learn/paths` | `ProgramsComponent` | Authenticated | View learning paths | `/api/programs` | Shared component needs learner presentation. |
| `/learn/certificates` | `CertificationsComponent` | Authenticated | View certificates | certification APIs | Needs child-friendly achievements framing. |
| `/learn/resources` | `LearnerResourcesComponent` | Authenticated | Access supporting resources | V2 product/resource APIs | Needs search/filter and source safety guidance. |
| `/learn/lesson/:id` | `LessonViewComponent` | Authenticated | Complete lesson | progress + lesson APIs | Should be canonical student lesson route. |

## Duplicate Pattern Register

| Domain | Duplicate routes/components | Proposed resolution |
| --- | --- | --- |
| Student learning | `/home`, `/home/courses`, `/home/lesson/:id`, `/learn/**` | Make `/learn` canonical for students; keep `/home` as compatibility redirect during implementation. |
| Course authoring | `/home/courses/new`, `/home/admin/courses`, `/home/studio/courses`, `/workspace/product-studio/courses` | Place authoring under Studio for content roles and Teach for teachers; admin sees governance summaries. |
| Sections/classes | `/home/sections`, `/workspace/learners/cohorts` | Teacher IA label "Classes"; retain section API names. |
| User management | `/home/admin/users`, `/workspace/learners/users` | Admin IA primary route; staff roster views remain class-scoped. |
| Settings | `/home/me/preferences`, `/workspace/settings` | Global profile route plus role-specific org/admin settings. |
