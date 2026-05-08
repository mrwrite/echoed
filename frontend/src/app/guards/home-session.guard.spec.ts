import { TestBed } from '@angular/core/testing';
import { Router, UrlTree } from '@angular/router';
import { HomeSessionGuard } from './home-session.guard';
import { AuthService } from '../services/auth.service';
import { PermissionsService } from '../services/permissions.service';
import { BootstrapOutcome } from '../services/permissions.service';

class MockAuthService {
  getToken(): string | null {
    return 'token';
  }
}

describe('HomeSessionGuard', () => {
  let guard: HomeSessionGuard;
  let permissionsService: jasmine.SpyObj<PermissionsService>;
  let parseUrlSpy: jasmine.Spy<(url: string) => UrlTree>;
  let onboardingTree: UrlTree;
  let loginTree: UrlTree;

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
    permissionsService = jasmine.createSpyObj<PermissionsService>('PermissionsService', ['bootstrapSession', 'getCurrentOutcome']);
    permissionsService.bootstrapSession.and.resolveTo();
    permissionsService.getCurrentOutcome.and.returnValue(readyOutcome);

    onboardingTree = { toString: () => '/onboarding/organization' } as UrlTree;
    loginTree = { toString: () => '/login' } as UrlTree;
    parseUrlSpy = jasmine.createSpy('parseUrl').and.callFake((url: string) => {
      if (url === '/onboarding/organization') {
        return onboardingTree;
      }
      if (url === '/login') {
        return loginTree;
      }
      return { toString: () => url } as UrlTree;
    });

    TestBed.configureTestingModule({
      providers: [
        HomeSessionGuard,
        { provide: AuthService, useClass: MockAuthService },
        { provide: PermissionsService, useValue: permissionsService },
        {
          provide: Router,
          useValue: {
            parseUrl: parseUrlSpy,
          },
        },
      ],
    });

    guard = TestBed.inject(HomeSessionGuard);
    sessionStorage.clear();
  });

  it('allows ready bootstrap outcomes', async () => {
    permissionsService.getCurrentOutcome.and.returnValue(readyOutcome);

    const result = await guard.canActivate();

    expect(result).toBe(true);
  });

  it('redirects onboardingRequired bootstrap outcomes', async () => {
    permissionsService.getCurrentOutcome.and.returnValue({
      ...readyOutcome,
      status: 'onboardingRequired',
      onboardingRequired: true,
    });

    const result = await guard.canActivate();

    expect(result).toBe(onboardingTree);
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

    const result = await guard.canActivate();

    expect(result).toBe(loginTree);
  });

  it('redirects failed bootstrap outcomes to login instead of falling through to home', async () => {
    permissionsService.getCurrentOutcome.and.returnValue({
      ...readyOutcome,
      status: 'failed',
      ready: false,
      failed: true,
      error: 'org_hydration_failed',
    });

    const result = await guard.canActivate();

    expect(result).toBe(loginTree);
  });

  it('redirects to login when no token is present before bootstrap', async () => {
    const authService = TestBed.inject(AuthService) as unknown as MockAuthService;
    spyOn(authService, 'getToken').and.returnValue(null);

    const result = await guard.canActivate();

    expect(result).toBe(loginTree);
    expect(permissionsService.bootstrapSession).not.toHaveBeenCalled();
  });

  it('does not silently fall through to home on org-refresh/bootstrap failure', async () => {
    permissionsService.getCurrentOutcome.and.returnValue({
      ...readyOutcome,
      status: 'failed',
      ready: false,
      failed: true,
      error: 'org_hydration_failed',
    });

    const result = await guard.canActivate();

    expect(result).not.toBe(true);
    expect(result).toBe(loginTree);
  });

  it('preserves super-admin-equivalent ready outcomes', async () => {
    permissionsService.getCurrentOutcome.and.returnValue({
      ...readyOutcome,
      activeOrgId: null,
      activeOrgRole: null,
      organizations: [],
    });

    const result = await guard.canActivate();

    expect(result).toBe(true);
  });
});
