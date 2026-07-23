import { Routes } from '@angular/router';
import { RoleGuard } from './guards/role.guard';
import { HomeSessionGuard } from './guards/home-session.guard';

const AccessDeniedComponent = () => import('./pages/access-denied/access-denied.component').then((m) => m.AccessDeniedComponent);
const AccessGrantsComponent = () => import('./pages/access-grants/access-grants.component').then((m) => m.AccessGrantsComponent);
const AdminBadgesComponent = () => import('./pages/admin-badges/admin-badges.component').then((m) => m.AdminBadgesComponent);
const AdminCoursesComponent = () => import('./pages/admin-courses/admin-courses.component').then((m) => m.AdminCoursesComponent);
const AdminOrganizationsComponent = () => import('./pages/admin-organizations/admin-organizations.component').then((m) => m.AdminOrganizationsComponent);
const AdminOverviewComponent = () => import('./pages/admin-overview/admin-overview.component').then((m) => m.AdminOverviewComponent);
const AdminReportsComponent = () => import('./pages/admin-reports/admin-reports.component').then((m) => m.AdminReportsComponent);
const AdminUserDetailComponent = () => import('./pages/admin-user-detail/admin-user-detail.component').then((m) => m.AdminUserDetailComponent);
const AdminUsersComponent = () => import('./pages/admin-users/admin-users.component').then((m) => m.AdminUsersComponent);
const ArtifactDetailComponent = () => import('./pages/artifact-detail/artifact-detail.component').then((m) => m.ArtifactDetailComponent);
const AssessmentDetailComponent = () => import('./pages/assessment-detail/assessment-detail.component').then((m) => m.AssessmentDetailComponent);
const AvailableCoursesComponent = () => import('./pages/available-courses/available-courses.component').then((m) => m.AvailableCoursesComponent);
const CertificationsComponent = () => import('./pages/certifications/certifications.component').then((m) => m.CertificationsComponent);
const CommercialDashboardComponent = () => import('./pages/commercial-dashboard/commercial-dashboard.component').then((m) => m.CommercialDashboardComponent);
const CourseWizardComponent = () => import('./pages/admin/course-wizard/course-wizard.component').then((m) => m.CourseWizardComponent);
const DemoReadinessComponent = () => import('./pages/demo-readiness/demo-readiness.component').then((m) => m.DemoReadinessComponent);
const EchoedRoleSelectorComponent = () => import('./pages/user-dashboard/echoed-role-selector/echoed-role-selector.component').then((m) => m.EchoedRoleSelectorComponent);
const GenerationRunDetailComponent = () => import('./pages/generation-run-detail/generation-run-detail.component').then((m) => m.GenerationRunDetailComponent);
const HomeComponent = () => import('./pages/home/home.component').then((m) => m.HomeComponent);
const LandingComponent = () => import('./pages/landing/landing.component').then((m) => m.LandingComponent);
const LearnerPortalComponent = () => import('./pages/learner-portal/learner-portal.component').then((m) => m.LearnerPortalComponent);
const LearnerProductsComponent = () => import('./pages/learner-portal/learner-products.component').then((m) => m.LearnerProductsComponent);
const LearnerResourcesComponent = () => import('./pages/learner-portal/learner-resources.component').then((m) => m.LearnerResourcesComponent);
const LessonViewComponent = () => import('./pages/lesson-view.component').then((m) => m.LessonViewComponent);
const LoginComponent = () => import('./pages/login/login.component').then((m) => m.LoginComponent);
const OnboardingOrganizationComponent = () => import('./pages/onboarding-organization/onboarding-organization.component').then((m) => m.OnboardingOrganizationComponent);
const OrganizationCoursesComponent = () => import('./pages/organization-courses/organization-courses.component').then((m) => m.OrganizationCoursesComponent);
const OrganizationInvitationsComponent = () => import('./pages/organization-invitations/organization-invitations.component').then((m) => m.OrganizationInvitationsComponent);
const OrganizationOverviewComponent = () => import('./pages/organization-overview/organization-overview.component').then((m) => m.OrganizationOverviewComponent);
const OrganizationPeopleComponent = () => import('./pages/organization-people/organization-people.component').then((m) => m.OrganizationPeopleComponent);
const OrganizationSectionDetailComponent = () => import('./pages/organization-section-detail/organization-section-detail.component').then((m) => m.OrganizationSectionDetailComponent);
const OrganizationSectionsComponent = () => import('./pages/organization-sections/organization-sections.component').then((m) => m.OrganizationSectionsComponent);
const OrganizationSettingsComponent = () => import('./pages/organization-settings/organization-settings.component').then((m) => m.OrganizationSettingsComponent);
const OrgInvitesComponent = () => import('./pages/org-invites/org-invites.component').then((m) => m.OrgInvitesComponent);
const PreferencesComponent = () => import('./pages/preferences/preferences.component').then((m) => m.PreferencesComponent);
const ProductDetailComponent = () => import('./pages/product-detail/product-detail.component').then((m) => m.ProductDetailComponent);
const ProductStudioComponent = () => import('./pages/product-studio/product-studio.component').then((m) => m.ProductStudioComponent);
const ProgramsComponent = () => import('./pages/programs/programs.component').then((m) => m.ProgramsComponent);
const ProjectDetailComponent = () => import('./pages/project-detail/project-detail.component').then((m) => m.ProjectDetailComponent);
const PublicProductDetailComponent = () => import('./pages/public-products/public-product-detail.component').then((m) => m.PublicProductDetailComponent);
const PublicProductsComponent = () => import('./pages/public-products/public-products.component').then((m) => m.PublicProductsComponent);
const RegistrationComponent = () => import('./pages/registration/registration.component').then((m) => m.RegistrationComponent);
const ReviewCenterComponent = () => import('./pages/review-center/review-center.component').then((m) => m.ReviewCenterComponent);
const RouteLoadErrorComponent = () => import('./pages/route-load-error/route-load-error.component').then((m) => m.RouteLoadErrorComponent);
const SectionDetailComponent = () => import('./pages/section-detail/section-detail.component').then((m) => m.SectionDetailComponent);
const SectionsComponent = () => import('./pages/sections/sections.component').then((m) => m.SectionsComponent);
const StudentCourseOverviewComponent = () => import('./pages/learner-portal/student-course-overview.component').then((m) => m.StudentCourseOverviewComponent);
const StudioContentDetailComponent = () => import('./pages/studio-content-detail/studio-content-detail.component').then((m) => m.StudioContentDetailComponent);
const StudioCoursesComponent = () => import('./pages/studio-courses/studio-courses.component').then((m) => m.StudioCoursesComponent);
const StudioCreateComponent = () => import('./pages/studio-create/studio-create.component').then((m) => m.StudioCreateComponent);
const StudioDraftDetailComponent = () => import('./pages/studio-draft-detail/studio-draft-detail.component').then((m) => m.StudioDraftDetailComponent);
const StudioLibraryComponent = () => import('./pages/studio-library/studio-library.component').then((m) => m.StudioLibraryComponent);
const StudioOverviewComponent = () => import('./pages/studio-overview/studio-overview.component').then((m) => m.StudioOverviewComponent);
const StudioProjectDetailComponent = () => import('./pages/studio-project-detail/studio-project-detail.component').then((m) => m.StudioProjectDetailComponent);
const StudioReviewComponent = () => import('./pages/studio-review/studio-review.component').then((m) => m.StudioReviewComponent);
const TeacherCoursePreviewComponent = () => import('./pages/teacher-curriculum/teacher-course-preview.component').then((m) => m.TeacherCoursePreviewComponent);
const TeacherCurriculumComponent = () => import('./pages/teacher-curriculum/teacher-curriculum.component').then((m) => m.TeacherCurriculumComponent);
const TeacherLearnerDetailComponent = () => import('./pages/teacher-learner-detail/teacher-learner-detail.component').then((m) => m.TeacherLearnerDetailComponent);
const UserDashboardComponent = () => import('./pages/user-dashboard/user-dashboard.component').then((m) => m.UserDashboardComponent);
const V2CollectionPageComponent = () => import('./pages/v2-platform/v2-collection-page.component').then((m) => m.V2CollectionPageComponent);
const WorkspaceAnalyticsComponent = () => import('./pages/workspace-analytics/workspace-analytics.component').then((m) => m.WorkspaceAnalyticsComponent);
const WorkspaceDashboardComponent = () => import('./pages/workspace-dashboard/workspace-dashboard.component').then((m) => m.WorkspaceDashboardComponent);

const creatorRoles = ['admin', 'teacher', 'content_admin', 'org_admin', 'instructor'];
const studioRoles = ['content_admin', 'org_admin'];
const sectionRoles = ['teacher', 'org_admin', 'instructor'];

export const routes: Routes = [
  { path: '', loadComponent: LandingComponent },
  { path: 'products', loadComponent: PublicProductsComponent },
  { path: 'products/:slug', loadComponent: PublicProductDetailComponent },
  { path: 'login', loadComponent: LoginComponent },
  { path: 'registration', loadComponent: RegistrationComponent },
  { path: 'onboarding/organization', loadComponent: OnboardingOrganizationComponent },
  { path: 'access-denied', loadComponent: AccessDeniedComponent },
  { path: 'load-error', loadComponent: RouteLoadErrorComponent },
  {
    path: 'admin',
    loadComponent: HomeComponent,
    canActivate: [HomeSessionGuard],
    children: [
      { path: '', loadComponent: AdminOverviewComponent, canActivate: [RoleGuard], data: { roles: ['admin', 'super_admin'] } },
      { path: 'users', loadComponent: AdminUsersComponent, canActivate: [RoleGuard], data: { roles: ['admin'] } },
      { path: 'users/:userId', loadComponent: AdminUserDetailComponent, canActivate: [RoleGuard], data: { roles: ['admin'] } },
      { path: 'organizations', loadComponent: AdminOrganizationsComponent, canActivate: [RoleGuard], data: { roles: ['admin', 'super_admin'] } },
      { path: 'organizations/:organizationId', loadComponent: AdminOrganizationsComponent, canActivate: [RoleGuard], data: { roles: ['admin', 'super_admin'] } },
      { path: 'courses', loadComponent: AdminCoursesComponent, canActivate: [RoleGuard], data: { roles: ['admin'] } },
      { path: 'courses/:courseId', loadComponent: AdminCoursesComponent, canActivate: [RoleGuard], data: { roles: ['admin'] } },
      { path: 'badges', loadComponent: AdminBadgesComponent, canActivate: [RoleGuard], data: { roles: ['admin', 'super_admin'] } },
      { path: 'reports', loadComponent: AdminReportsComponent, canActivate: [RoleGuard], data: { roles: ['admin'] } },
    ],
  },
  {
    path: 'studio',
    loadComponent: HomeComponent,
    canActivate: [HomeSessionGuard],
    children: [
      { path: '', loadComponent: StudioOverviewComponent, canActivate: [RoleGuard], data: { roles: ['content_admin'] } },
      { path: 'create', loadComponent: StudioCreateComponent, canActivate: [RoleGuard], data: { roles: ['content_admin'] } },
      { path: 'projects', loadComponent: StudioLibraryComponent, canActivate: [RoleGuard], data: { roles: ['content_admin'], mode: 'projects' } },
      { path: 'projects/:projectId', loadComponent: StudioProjectDetailComponent, canActivate: [RoleGuard], data: { roles: ['content_admin'] } },
      { path: 'content', loadComponent: StudioLibraryComponent, canActivate: [RoleGuard], data: { roles: ['content_admin'], mode: 'content' } },
      { path: 'content/:productId', loadComponent: StudioContentDetailComponent, canActivate: [RoleGuard], data: { roles: ['content_admin'] } },
      { path: 'courses', loadComponent: StudioLibraryComponent, canActivate: [RoleGuard], data: { roles: ['content_admin'], mode: 'courses' } },
      { path: 'programs', loadComponent: StudioLibraryComponent, canActivate: [RoleGuard], data: { roles: ['content_admin'], mode: 'programs' } },
      { path: 'sources', loadComponent: StudioLibraryComponent, canActivate: [RoleGuard], data: { roles: ['content_admin'], mode: 'sources' } },
      { path: 'drafts', loadComponent: StudioLibraryComponent, canActivate: [RoleGuard], data: { roles: ['content_admin'], mode: 'drafts' } },
      { path: 'drafts/:artifactId', loadComponent: StudioDraftDetailComponent, canActivate: [RoleGuard], data: { roles: ['content_admin'] } },
      { path: 'review', loadComponent: StudioReviewComponent, canActivate: [RoleGuard], data: { roles: ['content_admin'] } },
      { path: 'publishing', loadComponent: StudioLibraryComponent, canActivate: [RoleGuard], data: { roles: ['content_admin'], mode: 'publishing' } },
    ],
  },
  {
    path: 'organization',
    loadComponent: HomeComponent,
    canActivate: [HomeSessionGuard],
    children: [
      { path: '', loadComponent: OrganizationOverviewComponent, canActivate: [RoleGuard], data: { roles: ['org_admin'] } },
      { path: 'members', loadComponent: OrganizationPeopleComponent, canActivate: [RoleGuard], data: { roles: ['org_admin'], mode: 'members' } },
      { path: 'teachers', loadComponent: OrganizationPeopleComponent, canActivate: [RoleGuard], data: { roles: ['org_admin'], mode: 'teachers' } },
      { path: 'students', loadComponent: OrganizationPeopleComponent, canActivate: [RoleGuard], data: { roles: ['org_admin'], mode: 'students' } },
      { path: 'invitations', loadComponent: OrganizationInvitationsComponent, canActivate: [RoleGuard], data: { roles: ['org_admin'] } },
      { path: 'sections', loadComponent: OrganizationSectionsComponent, canActivate: [RoleGuard], data: { roles: ['org_admin'] } },
      { path: 'sections/:sectionId', loadComponent: OrganizationSectionDetailComponent, canActivate: [RoleGuard], data: { roles: ['org_admin'] } },
      { path: 'courses', loadComponent: OrganizationCoursesComponent, canActivate: [RoleGuard], data: { roles: ['org_admin'] } },
      { path: 'settings', loadComponent: OrganizationSettingsComponent, canActivate: [RoleGuard], data: { roles: ['org_admin'] } },
    ],
  },
  {
    path: 'teach',
    loadComponent: HomeComponent,
    canActivate: [HomeSessionGuard],
    children: [
      {
        path: '',
        loadComponent: UserDashboardComponent,
        children: [
          { path: '', loadComponent: EchoedRoleSelectorComponent },
          {
            path: 'classes',
            loadComponent: SectionsComponent,
            canActivate: [RoleGuard],
            data: { roles: ['teacher', 'instructor', 'org_admin'] }
          },
          {
            path: 'classes/:id',
            loadComponent: SectionDetailComponent,
            canActivate: [RoleGuard],
            data: { roles: ['teacher', 'instructor', 'org_admin'] }
          },
          {
            path: 'curriculum',
            loadComponent: TeacherCurriculumComponent,
            canActivate: [RoleGuard],
            data: { roles: ['teacher', 'instructor'] }
          },
          {
            path: 'courses/:courseId/preview',
            loadComponent: TeacherCoursePreviewComponent,
            canActivate: [RoleGuard],
            data: { roles: ['teacher', 'instructor'] }
          },
          {
            path: 'assignments',
            loadComponent: SectionsComponent,
            canActivate: [RoleGuard],
            data: { roles: ['teacher', 'instructor', 'org_admin'] }
          },
          {
            path: 'learners/:learnerId',
            loadComponent: TeacherLearnerDetailComponent,
            canActivate: [RoleGuard],
            data: { roles: ['teacher', 'instructor', 'org_admin'] }
          },
          { path: 'settings', loadComponent: PreferencesComponent },
        ]
      }
    ]
  },
  {
    path: 'home',
    loadComponent: HomeComponent,
    canActivate: [HomeSessionGuard],
    children: [
      {
        path: '',
        loadComponent: UserDashboardComponent,
        children: [
          { path: '', loadComponent: EchoedRoleSelectorComponent },
          {
            path: 'courses/new',
            loadComponent: CourseWizardComponent,
            canActivate: [RoleGuard],
            data: { roles: ['admin', 'teacher'] }
          },
          {
            path: 'courses/:courseId/edit',
            loadComponent: CourseWizardComponent,
            canActivate: [RoleGuard],
            data: { roles: ['admin', 'teacher'] }
          },
          { path: 'courses', loadComponent: AvailableCoursesComponent },
          { path: 'programs', loadComponent: ProgramsComponent },
          { path: 'assessments/:id', loadComponent: AssessmentDetailComponent },
          { path: 'certifications', loadComponent: CertificationsComponent },
          {
            path: 'org/invites',
            loadComponent: OrgInvitesComponent,
            canActivate: [RoleGuard],
            data: { roles: ['org_admin', 'content_admin'] }
          },
          {
            path: 'studio/courses',
            loadComponent: StudioCoursesComponent,
            canActivate: [RoleGuard],
            data: { roles: ['content_admin', 'org_admin'] }
          },
          {
            path: 'sections',
            loadComponent: SectionsComponent,
            canActivate: [RoleGuard],
            data: { roles: ['teacher', 'org_admin', 'instructor'] }
          },
          {
            path: 'sections/:id',
            loadComponent: SectionDetailComponent,
            canActivate: [RoleGuard],
            data: { roles: ['teacher', 'org_admin', 'instructor'] }
          },
          { path: 'me/preferences', loadComponent: PreferencesComponent },
          {
            path: 'admin/courses',
            loadComponent: AdminCoursesComponent,
            canActivate: [RoleGuard],
            data: { roles: ['admin'] }
          },
          {
            path: 'admin/badges',
            loadComponent: AdminBadgesComponent,
            canActivate: [RoleGuard],
            data: { roles: ['admin'] }
          },
          {
            path: 'admin/users',
            loadComponent: AdminUsersComponent,
            canActivate: [RoleGuard],
            data: { roles: ['admin'] }
          },
          { path: 'lesson/:id', loadComponent: LessonViewComponent },
        ]
      }
    ]
  },
  {
    path: 'workspace',
    loadComponent: HomeComponent,
    canActivate: [HomeSessionGuard],
    children: [
      {
        path: '',
        loadComponent: WorkspaceDashboardComponent,
        canActivate: [RoleGuard],
        data: { roles: creatorRoles }
      },
      {
        path: 'projects',
        loadComponent: V2CollectionPageComponent,
        canActivate: [RoleGuard],
        data: {
          roles: creatorRoles,
          eyebrow: 'Projects',
          title: 'Project knowledge pipeline',
          status: 'Real V2 project shell data. Creating projects is available through Product Studio.',
          emptyText: 'Create your first project shell from Product Studio.',
          collection: 'projects'
        }
      },
      {
        path: 'projects/:projectId',
        loadComponent: ProjectDetailComponent,
        canActivate: [RoleGuard],
        data: { roles: creatorRoles }
      },
      {
        path: 'product-studio',
        loadComponent: ProductStudioComponent,
        canActivate: [RoleGuard],
        data: { roles: creatorRoles }
      },
      {
        path: 'product-studio/create',
        loadComponent: ProductStudioComponent,
        canActivate: [RoleGuard],
        data: { roles: creatorRoles }
      },
      {
        path: 'product-studio/generation-runs',
        loadComponent: V2CollectionPageComponent,
        canActivate: [RoleGuard],
        data: {
          roles: creatorRoles,
          eyebrow: 'Generation Runs',
          title: 'AI generation attempts',
          status: 'Read-only generation metadata. Execution is not implemented in Phase 3.',
          emptyText: 'Generation run history will appear here after future AI execution workflows are implemented.',
          collection: 'generation-runs'
        }
      },
      {
        path: 'product-studio/generation-runs/:generationRunId',
        loadComponent: GenerationRunDetailComponent,
        canActivate: [RoleGuard],
        data: { roles: creatorRoles }
      },
      {
        path: 'product-studio/courses',
        loadComponent: StudioCoursesComponent,
        canActivate: [RoleGuard],
        data: { roles: studioRoles }
      },
      {
        path: 'product-studio/courses/new',
        loadComponent: CourseWizardComponent,
        canActivate: [RoleGuard],
        data: { roles: ['admin', 'teacher'] }
      },
      {
        path: 'product-studio/courses/:courseId/edit',
        loadComponent: CourseWizardComponent,
        canActivate: [RoleGuard],
        data: { roles: ['admin', 'teacher'] }
      },
      {
        path: 'products',
        loadComponent: V2CollectionPageComponent,
        canActivate: [RoleGuard],
        data: {
          roles: creatorRoles,
          eyebrow: 'Products',
          title: 'Product catalog',
          status: 'Real V2 product wrappers. Course-backed products link to the existing education runtime.',
          emptyText: 'Create product shells from Product Studio, or run the Phase 2 backfill migration for existing courses.',
          collection: 'products'
        }
      },
      {
        path: 'products/:productId',
        loadComponent: ProductDetailComponent,
        canActivate: [RoleGuard],
        data: { roles: creatorRoles }
      },
      {
        path: 'products/manage',
        loadComponent: AdminCoursesComponent,
        canActivate: [RoleGuard],
        data: { roles: ['admin'] }
      },
      {
        path: 'knowledge-sources',
        loadComponent: V2CollectionPageComponent,
        canActivate: [RoleGuard],
        data: {
          roles: creatorRoles,
          eyebrow: 'Knowledge Sources',
          title: 'Source-aware knowledge intake',
          status: 'Read-only knowledge source wrappers. Source import and management arrive in a later phase.',
          emptyText: 'No project-level knowledge sources exist yet.',
          collection: 'knowledge-sources'
        }
      },
      {
        path: 'artifacts',
        loadComponent: V2CollectionPageComponent,
        canActivate: [RoleGuard],
        data: {
          roles: creatorRoles,
          eyebrow: 'Artifacts',
          title: 'Generated documentation and learning assets',
          status: 'Read-only artifact wrappers. Review, packaging, and publishing arrive in later phases.',
          emptyText: 'No generated or uploaded artifacts exist yet.',
          collection: 'artifacts'
        }
      },
      {
        path: 'artifacts/:artifactId',
        loadComponent: ArtifactDetailComponent,
        canActivate: [RoleGuard],
        data: { roles: creatorRoles }
      },
      {
        path: 'review-center',
        loadComponent: ReviewCenterComponent,
        canActivate: [RoleGuard],
        data: { roles: creatorRoles }
      },
      {
        path: 'access',
        loadComponent: AccessGrantsComponent,
        canActivate: [RoleGuard],
        data: { roles: creatorRoles }
      },
      {
        path: 'learners',
        loadComponent: UserDashboardComponent,
        canActivate: [RoleGuard],
        data: { roles: creatorRoles },
        children: [
          { path: '', loadComponent: EchoedRoleSelectorComponent },
          { path: 'products', loadComponent: AvailableCoursesComponent },
          { path: 'paths', loadComponent: ProgramsComponent },
          { path: 'certificates', loadComponent: CertificationsComponent },
          {
            path: 'users',
            loadComponent: AdminUsersComponent,
            canActivate: [RoleGuard],
            data: { roles: ['admin'] }
          },
          {
            path: 'cohorts',
            loadComponent: SectionsComponent,
            canActivate: [RoleGuard],
            data: { roles: sectionRoles }
          },
          {
            path: 'cohorts/:id',
            loadComponent: SectionDetailComponent,
            canActivate: [RoleGuard],
            data: { roles: sectionRoles }
          }
        ]
      },
      {
        path: 'analytics',
        loadComponent: WorkspaceAnalyticsComponent,
        canActivate: [RoleGuard],
        data: { roles: creatorRoles }
      },
      {
        path: 'commercial',
        loadComponent: CommercialDashboardComponent,
        canActivate: [RoleGuard],
        data: { roles: creatorRoles }
      },
      {
        path: 'demo-readiness',
        loadComponent: DemoReadinessComponent,
        canActivate: [RoleGuard],
        data: { roles: creatorRoles }
      },
      {
        path: 'settings',
        loadComponent: PreferencesComponent,
        canActivate: [RoleGuard],
        data: { roles: creatorRoles }
      },
      {
        path: 'settings/invites',
        loadComponent: OrgInvitesComponent,
        canActivate: [RoleGuard],
        data: { roles: ['org_admin', 'content_admin'] }
      },
      {
        path: 'settings/badges',
        loadComponent: AdminBadgesComponent,
        canActivate: [RoleGuard],
        data: { roles: ['admin'] }
      },
      { path: 'lesson/:id', loadComponent: LessonViewComponent },
    ]
  },
  {
    path: 'learn',
    loadComponent: HomeComponent,
    canActivate: [HomeSessionGuard],
    children: [
      {
        path: '',
        loadComponent: UserDashboardComponent,
        children: [
          { path: '', loadComponent: LearnerPortalComponent },
          { path: 'products', loadComponent: LearnerProductsComponent },
          { path: 'courses/:courseId', loadComponent: StudentCourseOverviewComponent },
          { path: 'paths', loadComponent: ProgramsComponent },
          { path: 'certificates', loadComponent: CertificationsComponent },
          { path: 'resources', loadComponent: LearnerResourcesComponent },
          { path: 'lesson/:id', loadComponent: LessonViewComponent },
        ]
      }
    ]
  },
  { path: '**', redirectTo: '' }
];
