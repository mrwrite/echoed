import { Route, Routes } from '@angular/router';
import { routes } from './app.routes';
import { RoleGuard } from './guards/role.guard';

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

async function expectLazyComponent(route: Route | undefined, expectedName: string): Promise<void> {
  expect(route).toBeTruthy();
  expect(route?.component).toBeUndefined();
  expect(route?.loadComponent).toEqual(jasmine.any(Function));
  const component = await route!.loadComponent!();
  expect((component as { name?: string }).name).toBe(expectedName);
}

describe('app routes', () => {
  it('preserves the legacy authenticated home route', async () => {
    expect(findRoute(routes, 'home')).toBeTruthy();
    expect(findRoute(routes, 'home/')).toBeTruthy();
    await expectLazyComponent(findRoute(routes, 'products'), 'PublicProductsComponent');
    await expectLazyComponent(findRoute(routes, 'products/:slug'), 'PublicProductDetailComponent');
  });

  it('adds V2 workspace aliases for platform navigation', async () => {
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
    await expectLazyComponent(findRoute(routes, 'workspace/'), 'WorkspaceDashboardComponent');
    await expectLazyComponent(findRoute(routes, 'workspace/demo-readiness'), 'DemoReadinessComponent');
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

  it('adds canonical Teach aliases while preserving legacy teacher routes', async () => {
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

    await expectLazyComponent(findRoute(routes, 'teach/classes'), 'SectionsComponent');
    await expectLazyComponent(findRoute(routes, 'teach/classes/:id'), 'SectionDetailComponent');
    await expectLazyComponent(findRoute(routes, 'teach/curriculum'), 'TeacherCurriculumComponent');
    await expectLazyComponent(findRoute(routes, 'teach/courses/:courseId/preview'), 'TeacherCoursePreviewComponent');
    await expectLazyComponent(findRoute(routes, 'teach/learners/:learnerId'), 'TeacherLearnerDetailComponent');
    expect(findRoute(routes, 'teach/classes')?.canActivate).toContain(RoleGuard);
    expect(findRoute(routes, 'teach/curriculum')?.canActivate).toContain(RoleGuard);
  });

  it('adds guarded canonical Admin routes while preserving legacy aliases', async () => {
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

    await expectLazyComponent(findRoute(routes, 'admin/'), 'AdminOverviewComponent');
    await expectLazyComponent(findRoute(routes, 'admin/users'), 'AdminUsersComponent');
    await expectLazyComponent(findRoute(routes, 'admin/organizations'), 'AdminOrganizationsComponent');
    expect(findRoute(routes, 'admin/users')?.canActivate).toContain(RoleGuard);
    expect(findRoute(routes, 'admin/users')?.data?.['roles']).toEqual(['admin']);
    expect(findRoute(routes, 'admin/organizations')?.data?.['roles']).toEqual(['admin', 'super_admin']);
  });

  it('adds guarded canonical Studio routes while preserving workspace deep links', async () => {
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

    await expectLazyComponent(findRoute(routes, 'studio/'), 'StudioOverviewComponent');
    await expectLazyComponent(findRoute(routes, 'studio/courses'), 'StudioLibraryComponent');
    expect(findRoute(routes, 'studio/courses')?.canActivate).toContain(RoleGuard);
    expect(findRoute(routes, 'studio/courses')?.data?.['roles']).toEqual(['content_admin']);
  });

  it('adds guarded canonical Organization routes while preserving workspace deep links', async () => {
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

    await expectLazyComponent(findRoute(routes, 'organization/'), 'OrganizationOverviewComponent');
    await expectLazyComponent(findRoute(routes, 'organization/members'), 'OrganizationPeopleComponent');
    expect(findRoute(routes, 'organization/members')?.canActivate).toContain(RoleGuard);
    expect(findRoute(routes, 'organization/members')?.data?.['roles']).toEqual(['org_admin']);
  });

  it('maps Learner Portal V2 routes to lazy V2 pages while reusing lesson runtime', async () => {
    const learnRoute = findRoute(routes, 'learn');
    const learnerShell = learnRoute?.children?.find(route => route.path === '');
    await expectLazyComponent(learnerShell?.children?.find(route => route.path === ''), 'LearnerPortalComponent');
    await expectLazyComponent(learnerShell?.children?.find(route => route.path === 'products'), 'LearnerProductsComponent');
    await expectLazyComponent(learnerShell?.children?.find(route => route.path === 'courses/:courseId'), 'StudentCourseOverviewComponent');
    await expectLazyComponent(learnerShell?.children?.find(route => route.path === 'resources'), 'LearnerResourcesComponent');
    const learnerLesson = learnerShell?.children?.find(route => route.path === 'lesson/:id');
    const legacyLesson = findRoute(routes, 'home/lesson/:id');
    await expectLazyComponent(learnerLesson, 'LessonViewComponent');
    await expectLazyComponent(legacyLesson, 'LessonViewComponent');
    expect(learnerLesson?.loadComponent).toBe(legacyLesson?.loadComponent);
  });
});
