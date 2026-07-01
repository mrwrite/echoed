import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { UserDashboardComponent } from './pages/user-dashboard/user-dashboard.component';
import { RegistrationComponent } from './pages/registration/registration.component';
import { HomeComponent } from './pages/home/home.component';
import { CourseWizardComponent } from './pages/admin/course-wizard/course-wizard.component';
import { EchoedRoleSelectorComponent } from './pages/user-dashboard/echoed-role-selector/echoed-role-selector.component';
import { LessonViewComponent } from './pages/lesson-view.component';
import { LandingComponent } from './pages/landing/landing.component';
import { AvailableCoursesComponent } from './pages/available-courses/available-courses.component';
import { AdminUsersComponent } from './pages/admin-users/admin-users.component';
import { AdminCoursesComponent } from './pages/admin-courses/admin-courses.component';
import { AdminBadgesComponent } from './pages/admin-badges/admin-badges.component';
import { RoleGuard } from './guards/role.guard';
import { AccessDeniedComponent } from './pages/access-denied/access-denied.component';
import { OrgInvitesComponent } from './pages/org-invites/org-invites.component';
import { StudioCoursesComponent } from './pages/studio-courses/studio-courses.component';
import { SectionsComponent } from './pages/sections/sections.component';
import { SectionDetailComponent } from './pages/section-detail/section-detail.component';
import { PreferencesComponent } from './pages/preferences/preferences.component';
import { OnboardingOrganizationComponent } from './pages/onboarding-organization/onboarding-organization.component';
import { HomeSessionGuard } from './guards/home-session.guard';
import { ProgramsComponent } from './pages/programs/programs.component';
import { AssessmentDetailComponent } from './pages/assessment-detail/assessment-detail.component';
import { CertificationsComponent } from './pages/certifications/certifications.component';
import { V2PlatformPageComponent } from './pages/v2-platform/v2-platform-page.component';
import { ProductStudioComponent } from './pages/product-studio/product-studio.component';
import { V2CollectionPageComponent } from './pages/v2-platform/v2-collection-page.component';
import { ProductDetailComponent } from './pages/product-detail/product-detail.component';
import { ProjectDetailComponent } from './pages/project-detail/project-detail.component';
import { ArtifactDetailComponent } from './pages/artifact-detail/artifact-detail.component';
import { GenerationRunDetailComponent } from './pages/generation-run-detail/generation-run-detail.component';
import { ReviewCenterComponent } from './pages/review-center/review-center.component';
import { LearnerPortalComponent } from './pages/learner-portal/learner-portal.component';
import { LearnerProductsComponent } from './pages/learner-portal/learner-products.component';
import { LearnerResourcesComponent } from './pages/learner-portal/learner-resources.component';
import { AccessGrantsComponent } from './pages/access-grants/access-grants.component';
import { WorkspaceAnalyticsComponent } from './pages/workspace-analytics/workspace-analytics.component';
import { WorkspaceDashboardComponent } from './pages/workspace-dashboard/workspace-dashboard.component';
import { DemoReadinessComponent } from './pages/demo-readiness/demo-readiness.component';
import { PublicProductsComponent } from './pages/public-products/public-products.component';
import { PublicProductDetailComponent } from './pages/public-products/public-product-detail.component';
import { CommercialDashboardComponent } from './pages/commercial-dashboard/commercial-dashboard.component';

const creatorRoles = ['admin', 'teacher', 'content_admin', 'org_admin', 'instructor'];
const studioRoles = ['content_admin', 'org_admin'];
const sectionRoles = ['teacher', 'org_admin', 'instructor'];

export const routes: Routes = [
  { path: '', component: LandingComponent },
  { path: 'products', component: PublicProductsComponent },
  { path: 'products/:slug', component: PublicProductDetailComponent },
  { path: 'login', component: LoginComponent },
  { path: 'registration', component: RegistrationComponent },
  { path: 'onboarding/organization', component: OnboardingOrganizationComponent },
  { path: 'access-denied', component: AccessDeniedComponent },
  {
    path: 'home',
    component: HomeComponent,
    canActivate: [HomeSessionGuard],
    children: [
      {
        path: '',
        component: UserDashboardComponent,
        children: [
          { path: '', component: EchoedRoleSelectorComponent },
          {
            path: 'courses/new',
            component: CourseWizardComponent,
            canActivate: [RoleGuard],
            data: { roles: ['admin', 'teacher'] }
          },
          {
            path: 'courses/:courseId/edit',
            component: CourseWizardComponent,
            canActivate: [RoleGuard],
            data: { roles: ['admin', 'teacher'] }
          },
          { path: 'courses', component: AvailableCoursesComponent },
          { path: 'programs', component: ProgramsComponent },
          { path: 'assessments/:id', component: AssessmentDetailComponent },
          { path: 'certifications', component: CertificationsComponent },
          {
            path: 'org/invites',
            component: OrgInvitesComponent,
            canActivate: [RoleGuard],
            data: { roles: ['org_admin', 'content_admin'] }
          },
          {
            path: 'studio/courses',
            component: StudioCoursesComponent,
            canActivate: [RoleGuard],
            data: { roles: ['content_admin', 'org_admin'] }
          },
          {
            path: 'sections',
            component: SectionsComponent,
            canActivate: [RoleGuard],
            data: { roles: ['teacher', 'org_admin', 'instructor'] }
          },
          {
            path: 'sections/:id',
            component: SectionDetailComponent,
            canActivate: [RoleGuard],
            data: { roles: ['teacher', 'org_admin', 'instructor'] }
          },
          { path: 'me/preferences', component: PreferencesComponent },
          {
            path: 'admin/courses',
            component: AdminCoursesComponent,
            canActivate: [RoleGuard],
            data: { roles: ['admin'] }
          },
          {
            path: 'admin/badges',
            component: AdminBadgesComponent,
            canActivate: [RoleGuard],
            data: { roles: ['admin'] }
          },
          {
            path: 'admin/users',
            component: AdminUsersComponent,
            canActivate: [RoleGuard],
            data: { roles: ['admin'] }
          },
          { path: 'lesson/:id', component: LessonViewComponent },
        ]
      }
    ]
  },
  {
    path: 'workspace',
    component: HomeComponent,
    canActivate: [HomeSessionGuard],
    children: [
      {
        path: '',
        component: WorkspaceDashboardComponent,
      },
      {
        path: 'projects',
        component: V2CollectionPageComponent,
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
        component: ProjectDetailComponent,
        canActivate: [RoleGuard],
        data: { roles: creatorRoles }
      },
      {
        path: 'product-studio',
        component: ProductStudioComponent,
        canActivate: [RoleGuard],
        data: { roles: creatorRoles }
      },
      {
        path: 'product-studio/create',
        component: ProductStudioComponent,
        canActivate: [RoleGuard],
        data: { roles: creatorRoles }
      },
      {
        path: 'product-studio/generation-runs',
        component: V2CollectionPageComponent,
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
        component: GenerationRunDetailComponent,
        canActivate: [RoleGuard],
        data: { roles: creatorRoles }
      },
      {
        path: 'product-studio/courses',
        component: StudioCoursesComponent,
        canActivate: [RoleGuard],
        data: { roles: studioRoles }
      },
      {
        path: 'product-studio/courses/new',
        component: CourseWizardComponent,
        canActivate: [RoleGuard],
        data: { roles: ['admin', 'teacher'] }
      },
      {
        path: 'product-studio/courses/:courseId/edit',
        component: CourseWizardComponent,
        canActivate: [RoleGuard],
        data: { roles: ['admin', 'teacher'] }
      },
      {
        path: 'products',
        component: V2CollectionPageComponent,
        data: {
          eyebrow: 'Products',
          title: 'Product catalog',
          status: 'Real V2 product wrappers. Course-backed products link to the existing education runtime.',
          emptyText: 'Create product shells from Product Studio, or run the Phase 2 backfill migration for existing courses.',
          collection: 'products'
        }
      },
      {
        path: 'products/:productId',
        component: ProductDetailComponent,
      },
      {
        path: 'products/manage',
        component: AdminCoursesComponent,
        canActivate: [RoleGuard],
        data: { roles: ['admin'] }
      },
      {
        path: 'knowledge-sources',
        component: V2CollectionPageComponent,
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
        component: V2CollectionPageComponent,
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
        component: ArtifactDetailComponent,
        canActivate: [RoleGuard],
        data: { roles: creatorRoles }
      },
      {
        path: 'review-center',
        component: ReviewCenterComponent,
        canActivate: [RoleGuard],
        data: { roles: creatorRoles }
      },
      {
        path: 'access',
        component: AccessGrantsComponent,
        canActivate: [RoleGuard],
        data: { roles: creatorRoles }
      },
      {
        path: 'learners',
        component: UserDashboardComponent,
        children: [
          { path: '', component: EchoedRoleSelectorComponent },
          { path: 'products', component: AvailableCoursesComponent },
          { path: 'paths', component: ProgramsComponent },
          { path: 'certificates', component: CertificationsComponent },
          {
            path: 'users',
            component: AdminUsersComponent,
            canActivate: [RoleGuard],
            data: { roles: ['admin'] }
          },
          {
            path: 'cohorts',
            component: SectionsComponent,
            canActivate: [RoleGuard],
            data: { roles: sectionRoles }
          },
          {
            path: 'cohorts/:id',
            component: SectionDetailComponent,
            canActivate: [RoleGuard],
            data: { roles: sectionRoles }
          }
        ]
      },
      {
        path: 'analytics',
        component: WorkspaceAnalyticsComponent,
        canActivate: [RoleGuard],
        data: { roles: creatorRoles }
      },
      {
        path: 'commercial',
        component: CommercialDashboardComponent,
        canActivate: [RoleGuard],
        data: { roles: creatorRoles }
      },
      {
        path: 'demo-readiness',
        component: DemoReadinessComponent,
        canActivate: [RoleGuard],
        data: { roles: creatorRoles }
      },
      { path: 'settings', component: PreferencesComponent },
      {
        path: 'settings/invites',
        component: OrgInvitesComponent,
        canActivate: [RoleGuard],
        data: { roles: ['org_admin', 'content_admin'] }
      },
      {
        path: 'settings/badges',
        component: AdminBadgesComponent,
        canActivate: [RoleGuard],
        data: { roles: ['admin'] }
      },
      { path: 'lesson/:id', component: LessonViewComponent },
    ]
  },
  {
    path: 'learn',
    component: HomeComponent,
    canActivate: [HomeSessionGuard],
    children: [
      {
        path: '',
        component: UserDashboardComponent,
        children: [
          { path: '', component: LearnerPortalComponent },
          { path: 'products', component: LearnerProductsComponent },
          { path: 'paths', component: ProgramsComponent },
          { path: 'certificates', component: CertificationsComponent },
          { path: 'resources', component: LearnerResourcesComponent },
          { path: 'lesson/:id', component: LessonViewComponent },
        ]
      }
    ]
  },
  { path: '**', redirectTo: '' }
];
