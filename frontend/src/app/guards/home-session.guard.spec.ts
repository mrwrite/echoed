import { TestBed } from '@angular/core/testing';
import { Router, UrlTree } from '@angular/router';
import { BehaviorSubject, of } from 'rxjs';
import { HomeSessionGuard } from './home-session.guard';
import { AuthService } from '../services/auth.service';
import { PermissionsService } from '../services/permissions.service';
import { OrganizationService } from '../services/organization.service';

class MockAuthService {
  role = 'teacher';

  getToken() {
    return 'token';
  }

  getTokenPayload() {
    return { role: this.role };
  }

  isSuperAdminRole(role?: string) {
    return role === 'super_admin';
  }
}

class MockOrganizationService {
  refreshOrganizations = jasmine.createSpy('refreshOrganizations').and.returnValue(of([]));
}

describe('HomeSessionGuard', () => {
  let guard: HomeSessionGuard;
  let authService: MockAuthService;
  let organizationService: MockOrganizationService;
  let parseUrlSpy: jasmine.Spy<(url: string) => UrlTree>;
  let onboardingTree: UrlTree;

  beforeEach(() => {
    const ready$ = new BehaviorSubject<boolean>(true);
    const permissionsService = jasmine.createSpyObj<PermissionsService>('PermissionsService', ['bootstrapSession'], { ready$ });
    permissionsService.bootstrapSession.and.resolveTo();

    onboardingTree = { toString: () => '/onboarding/organization' } as UrlTree;
    parseUrlSpy = jasmine.createSpy('parseUrl').and.callFake((url: string) => {
      if (url === '/onboarding/organization') {
        return onboardingTree;
      }
      return { toString: () => url } as UrlTree;
    });

    TestBed.configureTestingModule({
      providers: [
        HomeSessionGuard,
        { provide: AuthService, useClass: MockAuthService },
        { provide: PermissionsService, useValue: permissionsService },
        { provide: OrganizationService, useClass: MockOrganizationService },
        {
          provide: Router,
          useValue: {
            parseUrl: parseUrlSpy,
          },
        },
      ],
    });

    guard = TestBed.inject(HomeSessionGuard);
    authService = TestBed.inject(AuthService) as unknown as MockAuthService;
    organizationService = TestBed.inject(OrganizationService) as unknown as MockOrganizationService;
    sessionStorage.removeItem('pending_org_creation');
  });

  it('redirects non-super-admin users with no org to onboarding', async () => {
    authService.role = 'teacher';
    organizationService.refreshOrganizations.and.returnValue(of([]));

    const result = await guard.canActivate();

    expect(parseUrlSpy).toHaveBeenCalledWith('/onboarding/organization');
    expect(result).toBe(onboardingTree);
  });

  it('allows super admins with no org to access dashboard shell', async () => {
    authService.role = 'super_admin';
    organizationService.refreshOrganizations.and.returnValue(of([]));

    const result = await guard.canActivate();

    expect(result).toBe(true);
    expect(parseUrlSpy).not.toHaveBeenCalledWith('/onboarding/organization');
  });
});
