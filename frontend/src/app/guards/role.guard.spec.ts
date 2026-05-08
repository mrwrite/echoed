import { TestBed } from '@angular/core/testing';
import { ActivatedRouteSnapshot, Router } from '@angular/router';
import { RoleGuard } from './role.guard';
import { PermissionsService, BootstrapOutcome } from '../services/permissions.service';

describe('RoleGuard', () => {
  let guard: RoleGuard;
  let permissionsService: jasmine.SpyObj<PermissionsService>;
  let router: jasmine.SpyObj<Router>;

  const readyOutcome: BootstrapOutcome = {
    status: 'ready',
    authenticated: true,
    ready: true,
    onboardingRequired: false,
    failed: false,
    activeOrgId: 'org-1',
    activeOrgRole: 'teacher',
    organizations: [{ id: 'org-1', type: 'school', role: 'teacher' }],
  };

  beforeEach(() => {
    permissionsService = jasmine.createSpyObj<PermissionsService>(
      'PermissionsService',
      ['bootstrapSession', 'hasAnyRole', 'getCurrentOutcome']
    );
    permissionsService.bootstrapSession.and.resolveTo();
    permissionsService.hasAnyRole.and.returnValue(true);
    permissionsService.getCurrentOutcome.and.returnValue(readyOutcome);

    router = jasmine.createSpyObj<Router>('Router', ['navigate']);
    router.navigate.and.resolveTo(true);

    TestBed.configureTestingModule({
      providers: [
        RoleGuard,
        { provide: PermissionsService, useValue: permissionsService },
        { provide: Router, useValue: router },
      ]
    });

    guard = TestBed.inject(RoleGuard);
  });

  it('uses canonical bootstrap/session state before allowing access', async () => {
    const canActivate = await guard.canActivate({ data: { roles: ['teacher'] } } as unknown as ActivatedRouteSnapshot);

    expect(permissionsService.bootstrapSession).toHaveBeenCalled();
    expect(permissionsService.getCurrentOutcome).toHaveBeenCalled();
    expect(canActivate).toBe(true);
  });

  it('redirects unauthenticated bootstrap outcomes to login', async () => {
    permissionsService.getCurrentOutcome.and.returnValue({
      ...readyOutcome,
      status: 'unauthenticated',
      authenticated: false,
      ready: false,
      activeOrgId: null,
      activeOrgRole: null,
      organizations: [],
    });

    const canActivate = await guard.canActivate({ data: { roles: ['teacher'] } } as unknown as ActivatedRouteSnapshot);

    expect(canActivate).toBe(false);
    expect(router.navigate).toHaveBeenCalledWith(['/login']);
  });

  it('redirects failed bootstrap outcomes to login', async () => {
    permissionsService.getCurrentOutcome.and.returnValue({
      ...readyOutcome,
      status: 'failed',
      ready: false,
      failed: true,
    });

    const canActivate = await guard.canActivate({ data: { roles: ['teacher'] } } as unknown as ActivatedRouteSnapshot);

    expect(canActivate).toBe(false);
    expect(router.navigate).toHaveBeenCalledWith(['/login']);
  });

  it('redirects onboardingRequired outcomes to onboarding', async () => {
    permissionsService.getCurrentOutcome.and.returnValue({
      ...readyOutcome,
      status: 'onboardingRequired',
      onboardingRequired: true,
    });

    const canActivate = await guard.canActivate({ data: { roles: ['teacher'] } } as unknown as ActivatedRouteSnapshot);

    expect(canActivate).toBe(false);
    expect(router.navigate).toHaveBeenCalledWith(['/onboarding/organization']);
  });

  it('allows access only when canonical permissions allow it', async () => {
    permissionsService.hasAnyRole.and.returnValue(false);

    const canActivate = await guard.canActivate({ data: { roles: ['admin'] } } as unknown as ActivatedRouteSnapshot);

    expect(canActivate).toBe(false);
    expect(router.navigate).toHaveBeenCalledWith(['/access-denied']);
  });
});
