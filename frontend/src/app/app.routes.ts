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

const creatorRoles = ['admin', 'teacher', 'content_admin', 'org_admin', 'instructor'];
const studioRoles = ['content_admin', 'org_admin'];
const sectionRoles = ['teacher', 'org_admin', 'instructor'];

export const routes: Routes = [
  { path: '', component: LandingComponent },
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
        component: V2PlatformPageComponent,
        data: {
          eyebrow: 'Workspace',
          title: 'EchoEd workspace',
          description: 'A platform view of your organization knowledge, learning products, review workflow, learners, and operational readiness.',
          status: 'Phase 1 maps the existing education runtime into the V2 platform shell without replacing courses, lessons, progress, or governance.',
          links: [
            { label: 'View products', route: '/workspace/products' },
            { label: 'Open learner portal', route: '/workspace/learners' },
            { label: 'Review center', route: '/workspace/review-center' }
          ]
        }
      },
      {
        path: 'projects',
        component: V2PlatformPageComponent,
        canActivate: [RoleGuard],
        data: {
          roles: creatorRoles,
          eyebrow: 'Projects',
          title: 'Project knowledge pipeline',
          description: 'Projects will group source material, AI analysis, generated artifacts, and product outputs for a business or technical initiative.',
          status: 'Placeholder route: wrapper models arrive in a later phase; existing course runtime remains unchanged.'
        }
      },
      {
        path: 'product-studio',
        component: V2PlatformPageComponent,
        canActivate: [RoleGuard],
        data: {
          roles: creatorRoles,
          eyebrow: 'Product Studio',
          title: 'Create trusted learning products',
          description: 'Product Studio will orchestrate source import, AI generation, human review, approval, publishing, and delivery.',
          status: 'Phase 1 exposes the Studio entry point and links to existing course creation tools.',
          links: [
            { label: 'Existing studio courses', route: '/workspace/product-studio/courses' },
            { label: 'Create course-backed product', route: '/workspace/product-studio/courses/new' }
          ]
        }
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
      { path: 'products', component: AvailableCoursesComponent },
      {
        path: 'products/manage',
        component: AdminCoursesComponent,
        canActivate: [RoleGuard],
        data: { roles: ['admin'] }
      },
      {
        path: 'knowledge-sources',
        component: V2PlatformPageComponent,
        canActivate: [RoleGuard],
        data: {
          roles: creatorRoles,
          eyebrow: 'Knowledge Sources',
          title: 'Source-aware knowledge intake',
          description: 'Knowledge Sources will collect documentation, project references, files, and source-backed material used by AI-assisted generation.',
          status: 'Placeholder route: source-backed lesson readiness remains available through existing governance flows.'
        }
      },
      {
        path: 'artifacts',
        component: V2PlatformPageComponent,
        canActivate: [RoleGuard],
        data: {
          roles: creatorRoles,
          eyebrow: 'Artifacts',
          title: 'Generated documentation and learning assets',
          description: 'Artifacts will track AI-generated documentation, playbooks, downloads, and reusable assets before they become learning products.',
          status: 'Placeholder route: artifact registry models and packaging workflows are planned for a later phase.'
        }
      },
      {
        path: 'review-center',
        component: V2PlatformPageComponent,
        canActivate: [RoleGuard],
        data: {
          roles: creatorRoles,
          eyebrow: 'Review Center',
          title: 'Governance and readiness review',
          description: 'Review Center will centralize source-backed lesson readiness, approvals, and product publishing confidence.',
          status: 'Phase 1 preserves existing governance behavior and provides links into current review-capable surfaces.',
          links: [
            { label: 'Studio courses', route: '/workspace/product-studio/courses' },
            { label: 'Managed products', route: '/workspace/products/manage' }
          ]
        }
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
        component: V2PlatformPageComponent,
        canActivate: [RoleGuard],
        data: {
          roles: creatorRoles,
          eyebrow: 'Analytics',
          title: 'Learner and product intelligence',
          description: 'Analytics V2 will connect progress, completion, readiness, and product performance into operational confidence views.',
          status: 'Placeholder route: existing progress tracking remains the runtime source of truth.'
        }
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
          { path: '', component: EchoedRoleSelectorComponent },
          { path: 'products', component: AvailableCoursesComponent },
          { path: 'paths', component: ProgramsComponent },
          { path: 'certificates', component: CertificationsComponent },
          {
            path: 'resources',
            component: V2PlatformPageComponent,
            data: {
              eyebrow: 'Resources',
              title: 'Knowledge resources',
              description: 'Downloadable documentation packs and knowledge hub resources will appear here as the V2 artifact registry comes online.',
              status: 'Placeholder route: current learner course and certification routes remain unchanged.'
            }
          },
          { path: 'lesson/:id', component: LessonViewComponent },
        ]
      }
    ]
  },
  { path: '**', redirectTo: '' }
];
