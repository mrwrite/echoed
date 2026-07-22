import { Route, Routes } from '@angular/router';
import { routes } from './app.routes';
import { LearnerPortalComponent } from './pages/learner-portal/learner-portal.component';
import { LearnerProductsComponent } from './pages/learner-portal/learner-products.component';
import { LearnerResourcesComponent } from './pages/learner-portal/learner-resources.component';
import { StudentCourseOverviewComponent } from './pages/learner-portal/student-course-overview.component';
import { LessonViewComponent } from './pages/lesson-view.component';
import { WorkspaceDashboardComponent } from './pages/workspace-dashboard/workspace-dashboard.component';
import { DemoReadinessComponent } from './pages/demo-readiness/demo-readiness.component';
import { PublicProductsComponent } from './pages/public-products/public-products.component';
import { PublicProductDetailComponent } from './pages/public-products/public-product-detail.component';
import { RoleGuard } from './guards/role.guard';
import { SectionsComponent } from './pages/sections/sections.component';
import { SectionDetailComponent } from './pages/section-detail/section-detail.component';
import { TeacherCurriculumComponent } from './pages/teacher-curriculum/teacher-curriculum.component';
import { TeacherCoursePreviewComponent } from './pages/teacher-curriculum/teacher-course-preview.component';
import { TeacherLearnerDetailComponent } from './pages/teacher-learner-detail/teacher-learner-detail.component';
import { AdminOverviewComponent } from './pages/admin-overview/admin-overview.component';
import { AdminUsersComponent } from './pages/admin-users/admin-users.component';
import { AdminOrganizationsComponent } from './pages/admin-organizations/admin-organizations.component';
import { StudioOverviewComponent } from './pages/studio-overview/studio-overview.component';
import { StudioLibraryComponent } from './pages/studio-library/studio-library.component';
import { OrganizationOverviewComponent } from './pages/organization-overview/organization-overview.component';
import { OrganizationPeopleComponent } from './pages/organization-people/organization-people.component';

function findRoute(routeList: Routes, path: string): Route | undefined {
  const exactRoute = routeList.find(candidate => candidate.path === path);
  if (exactRoute) {
    return exactRoute;
  }

  const [head, ...tail] = path.split('/');
  const route = routeList.find(candidate => candidate.path === head);

  if (!route) {
    const passthrough = routeList.find(candidate => candidate.path === '');
    return passthrough?.children ? findRoute(passthrough.children, path) : undefined;
  }

  if (tail.length === 0) {
    return route;
  }

  if (route.children) {
    return findRoute(route.children, tail.join('/'));
  }

  const passthrough = routeList.find(candidate => candidate.path === '');
  return passthrough?.children ? findRoute(passthrough.children, path) : undefined;
}

describe('app routes', () => {
  it('preserves the legacy authenticated home route', () => {
    expect(findRoute(routes, 'home')).toBeTruthy();
    expect(findRoute(routes, 'home/')).toBeTruthy();
    expect(findRoute(routes, 'products')?.component).toBe(PublicProductsComponent);
    expect(findRoute(routes, 'products/:slug')?.component).toBe(PublicProductDetailComponent);
  });

  it('adds V2 workspace aliases for platform navigation', () => {
    [
      'workspace',
      'workspace/projects',
      'workspace/projects/:projectId',
      'workspace/product-studio',
      'workspace/product-studio/create',
      'workspace/product-studio/courses/new',
      'workspace/product-studio/courses/:courseId/edit',
      'workspace/product-studio/generation-runs',
      'workspace/product-studio/generation-runs/:generationRunId',
      'workspace/products',
      'workspace/products/:productId',
      'workspace/knowledge-sources',
      'workspace/artifacts',
      'workspace/artifacts/:artifactId',
      'workspace/review-center',
      'workspace/access',
      'workspace/learners',
      'workspace/analytics',
      'workspace/commercial',
      'workspace/demo-readiness',
      'workspace/settings',
    ].forEach(path => expect(findRoute(routes, path)).withContext(path).toBeTruthy());
    expect(findRoute(routes, 'workspace/')?.component).toBe(WorkspaceDashboardComponent);
    expect(findRoute(routes, 'workspace/demo-readiness')?.component).toBe(DemoReadinessComponent);
    expect(findRoute(routes, 'workspace/')?.canActivate).toContain(RoleGuard);
    expect(findRoute(routes, 'workspace/products')?.canActivate).toContain(RoleGuard);
    expect(findRoute(routes, 'workspace/products/:productId')?.canActivate).toContain(RoleGuard);
    expect(findRoute(routes, 'workspace/learners')?.canActivate).toContain(RoleGuard);
  });

  it('adds learner portal aliases without removing existing learner pages', () => {
    [
      'learn',
      'learn/',
      'learn/products',
      'learn/courses/:courseId',
      'learn/paths',
      'learn/certificates',
      'learn/resources',
      'learn/lesson/:id',
    ].forEach(path => expect(findRoute(routes, path)).withContext(path).toBeTruthy());
  });

  it('adds canonical Teach aliases while preserving legacy teacher routes', () => {
    [
      'teach',
      'teach/',
      'teach/classes',
      'teach/classes/:id',
      'teach/curriculum',
      'teach/courses/:courseId/preview',
      'teach/assignments',
      'teach/learners/:learnerId',
      'home/sections',
      'home/sections/:id',
      'workspace/learners/cohorts',
      'workspace/learners/cohorts/:id',
    ].forEach(path => expect(findRoute(routes, path)).withContext(path).toBeTruthy());

    expect(findRoute(routes, 'teach/classes')?.component).toBe(SectionsComponent);
    expect(findRoute(routes, 'teach/classes/:id')?.component).toBe(SectionDetailComponent);
    expect(findRoute(routes, 'teach/curriculum')?.component).toBe(TeacherCurriculumComponent);
    expect(findRoute(routes, 'teach/courses/:courseId/preview')?.component).toBe(TeacherCoursePreviewComponent);
    expect(findRoute(routes, 'teach/learners/:learnerId')?.component).toBe(TeacherLearnerDetailComponent);
    expect(findRoute(routes, 'teach/classes')?.canActivate).toContain(RoleGuard);
    expect(findRoute(routes, 'teach/curriculum')?.canActivate).toContain(RoleGuard);
  });

  it('adds guarded canonical Admin routes while preserving legacy aliases', () => {
    [
      'admin',
      'admin/users',
      'admin/users/:userId',
      'admin/organizations',
      'admin/organizations/:organizationId',
      'admin/courses',
      'admin/courses/:courseId',
      'admin/badges',
      'admin/reports',
      'home/admin/users',
      'home/admin/courses',
      'home/admin/badges',
    ].forEach(path => expect(findRoute(routes, path)).withContext(path).toBeTruthy());

    expect(findRoute(routes, 'admin/')?.component).toBe(AdminOverviewComponent);
    expect(findRoute(routes, 'admin/users')?.component).toBe(AdminUsersComponent);
    expect(findRoute(routes, 'admin/organizations')?.component).toBe(AdminOrganizationsComponent);
    expect(findRoute(routes, 'admin/users')?.canActivate).toContain(RoleGuard);
    expect(findRoute(routes, 'admin/users')?.data?.['roles']).toEqual(['admin']);
    expect(findRoute(routes, 'admin/organizations')?.data?.['roles']).toEqual(['admin', 'super_admin']);
  });

  it('adds guarded canonical Studio routes while preserving workspace deep links', () => {
    [
      'studio',
      'studio/create',
      'studio/projects',
      'studio/projects/:projectId',
      'studio/content',
      'studio/content/:productId',
      'studio/courses',
      'studio/programs',
      'studio/sources',
      'studio/drafts',
      'studio/drafts/:artifactId',
      'studio/review',
      'studio/publishing',
      'workspace/product-studio',
      'workspace/products',
      'workspace/review-center',
    ].forEach(path => expect(findRoute(routes, path)).withContext(path).toBeTruthy());

    expect(findRoute(routes, 'studio/')?.component).toBe(StudioOverviewComponent);
    expect(findRoute(routes, 'studio/courses')?.component).toBe(StudioLibraryComponent);
    expect(findRoute(routes, 'studio/courses')?.canActivate).toContain(RoleGuard);
    expect(findRoute(routes, 'studio/courses')?.data?.['roles']).toEqual(['content_admin']);
  });

  it('adds guarded canonical Organization routes while preserving workspace deep links', () => {
    [
      'organization',
      'organization/members',
      'organization/teachers',
      'organization/students',
      'organization/invitations',
      'organization/sections',
      'organization/sections/:sectionId',
      'organization/courses',
      'organization/settings',
      'workspace/learners',
      'workspace/settings/invites',
      'workspace/learners/cohorts',
    ].forEach(path => expect(findRoute(routes, path)).withContext(path).toBeTruthy());

    expect(findRoute(routes, 'organization/')?.component).toBe(OrganizationOverviewComponent);
    expect(findRoute(routes, 'organization/members')?.component).toBe(OrganizationPeopleComponent);
    expect(findRoute(routes, 'organization/members')?.canActivate).toContain(RoleGuard);
    expect(findRoute(routes, 'organization/members')?.data?.['roles']).toEqual(['org_admin']);
  });

  it('maps Learner Portal V2 routes to V2 pages while reusing lesson runtime', () => {
    const learnRoute = findRoute(routes, 'learn');
    const learnerShell = learnRoute?.children?.find(route => route.path === '');
    expect(learnerShell?.children?.find(route => route.path === '')?.component).toBe(LearnerPortalComponent);
    expect(learnerShell?.children?.find(route => route.path === 'products')?.component).toBe(LearnerProductsComponent);
    expect(learnerShell?.children?.find(route => route.path === 'courses/:courseId')?.component).toBe(StudentCourseOverviewComponent);
    expect(learnerShell?.children?.find(route => route.path === 'resources')?.component).toBe(LearnerResourcesComponent);
    expect(learnerShell?.children?.find(route => route.path === 'lesson/:id')?.component).toBe(LessonViewComponent);
    expect(findRoute(routes, 'home/lesson/:id')?.component).toBe(LessonViewComponent);
  });
});
