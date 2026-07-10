import { TestBed } from '@angular/core/testing';

import { BootstrapOutcome, PermissionsService } from './permissions.service';
import { ShellNavigationService } from './shell-navigation.service';

class MockPermissionsService {
  private permissions = new Set<string>();
  private outcome: BootstrapOutcome = {
    status: 'ready',
    authenticated: true,
    ready: true,
    onboardingRequired: false,
    failed: false,
    activeOrgId: 'org-1',
    activeOrgRole: 'student',
    organizations: [],
  };

  getCurrentPermissions(): Set<string> {
    return this.permissions;
  }

  getCurrentOutcome(): BootstrapOutcome {
    return this.outcome;
  }

  setPermissions(values: string[]): void {
    this.permissions = new Set(values);
  }
}

describe('ShellNavigationService', () => {
  let service: ShellNavigationService;
  let permissionsService: MockPermissionsService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        ShellNavigationService,
        { provide: PermissionsService, useClass: MockPermissionsService },
      ],
    });

    service = TestBed.inject(ShellNavigationService);
    permissionsService = TestBed.inject(PermissionsService) as unknown as MockPermissionsService;
  });

  it('routes students to Learn as the canonical destination', () => {
    permissionsService.setPermissions(['role:student']);

    expect(service.canonicalRouteForCurrentUser()).toBe('/learn');
    expect(service.getPrimarySpace(new Set(['role:student'])).name).toBe('Learn');
  });

  it('maps teacher and instructor-compatible users to Teach navigation', () => {
    const teacherSections = service.visibleSections(new Set(['role:teacher']));
    const instructorSections = service.visibleSections(new Set(['role:instructor']));

    expect(teacherSections.map((section) => section.title)).toContain('Teach');
    expect(instructorSections.map((section) => section.title)).toEqual(['Teach']);
    expect(service.getPrimarySpace(new Set(['role:teacher'])).canonicalRoute).toBe('/home');
  });

  it('maps content administrators to education-oriented Studio labels', () => {
    const sections = service.visibleSections(new Set([
      'role:content_admin',
      'nav:workspace',
      'nav:product-studio',
      'nav:products',
      'nav:knowledge-sources',
    ]));
    const labels = sections.flatMap((section) => section.items.map((item) => item.label));

    expect(service.getPrimarySpace(new Set(['role:content_admin'])).name).toBe('Studio');
    expect(labels).toContain('Content Studio');
    expect(labels).toContain('Learning Products');
    expect(labels).toContain('Sources');
    expect(labels).not.toContain('Commercial');
  });

  it('maps organization administrators to Organization navigation', () => {
    const space = service.getPrimarySpace(new Set(['role:org_admin']));
    const labels = service
      .visibleSections(new Set(['role:org_admin', 'nav:cohorts', 'nav:settings']))
      .flatMap((section) => section.items.map((item) => item.label));

    expect(space.name).toBe('Organization');
    expect(space.canonicalRoute).toBe('/workspace/learners');
    expect(labels).toContain('Organization Home');
    expect(labels).toContain('Classes');
  });

  it('maps admins and super-admin-compatible users to Admin without inventing unsupported portals', () => {
    const adminLabels = service
      .visibleSections(new Set(['role:admin', 'nav:admin-users', 'nav:commercial']))
      .flatMap((section) => section.items.map((item) => item.label));
    const superAdminLabels = service
      .visibleSections(new Set(['role:super_admin']))
      .flatMap((section) => section.items.map((item) => item.label));

    expect(service.getPrimarySpace(new Set(['role:admin'])).name).toBe('Admin');
    expect(service.getPrimarySpace(new Set(['role:super_admin'])).name).toBe('Admin');
    expect(adminLabels).toContain('Community');
    expect(superAdminLabels).toEqual(['Admin Overview']);
  });

  it('does not expose navigation for unsupported parent or viewer roles', () => {
    expect(service.visibleSections(new Set(['role:parent']))).toEqual([]);
    expect(service.visibleSections(new Set(['role:viewer']))).toEqual([]);
  });
});
