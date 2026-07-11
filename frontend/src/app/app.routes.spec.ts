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
