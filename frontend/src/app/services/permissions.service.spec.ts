import { TestBed } from '@angular/core/testing';
import { BehaviorSubject, Observable, Subject, firstValueFrom, of, throwError } from 'rxjs';

import { PermissionsService } from './permissions.service';
import { AuthService } from './auth.service';
import { OrganizationService } from './organization.service';
import { RoleService } from './role.service';

class MockAuthService {
  token: string | null = 'token';
  payload: any = {
    sub: 'teacher',
    user_id: 'user-1',
    fullname: 'Teacher User',
    role: 'teacher',
    exp: Math.floor(Date.now() / 1000) + 3600,
  };
  expired = false;

  getToken() {
    return this.token;
  }

  getTokenPayload() {
    return this.payload;
  }

  isTokenExpired() {
    return this.expired;
  }

  isSuperAdminRole(role?: string | null) {
    return role === 'super_admin';
  }
}

class MockOrganizationService {
  private readonly organizationsSubject = new BehaviorSubject<any[]>([]);
  organizations$ = this.organizationsSubject.asObservable();
  refreshOrganizations = jasmine.createSpy('refreshOrganizations').and.returnValue(of([]));
  activeOrgId: string | null = null;
  activeOrgRole: string | null = null;

  get organizationsSubjectValue() {
    return this.organizationsSubject.value;
  }

  setOrganizations(orgs: any[]) {
    this.organizationsSubject.next(orgs);
  }

  getActiveOrgId() {
    return this.activeOrgId;
  }

  getActiveOrgRole() {
    return this.activeOrgRole;
  }
}

class MockRoleService {
  setUserRoles = jasmine.createSpy('setUserRoles');
}

describe('PermissionsService', () => {
  let service: PermissionsService;
  let authService: MockAuthService;
  let organizationService: MockOrganizationService;
  let roleService: MockRoleService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        PermissionsService,
        { provide: AuthService, useClass: MockAuthService },
        { provide: OrganizationService, useClass: MockOrganizationService },
        { provide: RoleService, useClass: MockRoleService },
      ],
    });

    service = TestBed.inject(PermissionsService);
    authService = TestBed.inject(AuthService) as unknown as MockAuthService;
    organizationService = TestBed.inject(OrganizationService) as unknown as MockOrganizationService;
    roleService = TestBed.inject(RoleService) as unknown as MockRoleService;
    localStorage.clear();
    sessionStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
    sessionStorage.clear();
  });

  it('produces a ready outcome for a valid token with a valid active org', async () => {
    organizationService.activeOrgId = 'org-2';
    organizationService.setOrganizations([
      { id: 'org-1', type: 'school', role: 'teacher' },
      { id: 'org-2', type: 'school', role: 'content_admin' },
    ]);

    await service.bootstrapSession();

    const outcome = service.getCurrentOutcome();
    expect(outcome.status).toBe('ready');
    expect(outcome.ready).toBeTrue();
    expect(outcome.activeOrgId).toBe('org-2');
    expect(outcome.activeOrgRole).toBe('content_admin');
    expect(service.hasAnyRole('content_admin')).toBeTrue();
    expect(service.hasAnyRole('teacher')).toBeTrue();
  });

  it('produces an unauthenticated outcome when the token is missing', async () => {
    authService.token = null;

    await service.bootstrapSession();

    const outcome = service.getCurrentOutcome();
    expect(outcome.status).toBe('unauthenticated');
    expect(outcome.ready).toBeFalse();
  });

  it('produces an unauthenticated outcome when the token is expired', async () => {
    authService.expired = true;

    await service.bootstrapSession();

    const outcome = service.getCurrentOutcome();
    expect(outcome.status).toBe('unauthenticated');
    expect(outcome.ready).toBeFalse();
    expect(outcome.error).toBe('expired_token');
  });

  it('produces an onboardingRequired outcome when organizations are missing', async () => {
    organizationService.refreshOrganizations.and.returnValue(of([]));

    await service.bootstrapSession();

    const outcome = service.getCurrentOutcome();
    expect(outcome.status).toBe('onboardingRequired');
    expect(outcome.onboardingRequired).toBeTrue();
    expect(outcome.ready).toBeTrue();
  });

  it('produces an onboardingRequired outcome for personal-only organizations', async () => {
    organizationService.activeOrgId = 'personal-1';
    organizationService.refreshOrganizations.and.returnValue(
      of([{ id: 'personal-1', type: 'personal', role: 'org_admin' }]),
    );

    await service.bootstrapSession();

    const outcome = service.getCurrentOutcome();
    expect(outcome.status).toBe('onboardingRequired');
    expect(outcome.onboardingRequired).toBeTrue();
    expect(outcome.ready).toBeTrue();
  });

  it('produces an onboardingRequired outcome when pending org setup exists', async () => {
    sessionStorage.setItem('pending_org_creation', JSON.stringify({ name: 'Bright Futures', type: 'school' }));
    organizationService.activeOrgId = 'school-1';
    organizationService.refreshOrganizations.and.returnValue(
      of([{ id: 'school-1', type: 'school', role: 'org_admin' }]),
    );

    await service.bootstrapSession();

    const outcome = service.getCurrentOutcome();
    expect(outcome.status).toBe('onboardingRequired');
    expect(outcome.onboardingRequired).toBeTrue();
  });

  it('produces a failed outcome when organization hydration fails', async () => {
    organizationService.refreshOrganizations.and.returnValue(
      throwError(() => new Error('org fetch failed')),
    );

    await service.bootstrapSession();

    const outcome = service.getCurrentOutcome();
    expect(outcome.status).toBe('failed');
    expect(outcome.failed).toBeTrue();
    expect(outcome.ready).toBeFalse();
    expect(outcome.error).toBe('org_hydration_failed');
  });

  it('deduplicates concurrent bootstrap calls', async () => {
    const refreshSubject = new Subject<any[]>();
    organizationService.refreshOrganizations.and.returnValue(refreshSubject.asObservable());
    const bootstrapOne = service.bootstrapSession();
    const bootstrapTwo = service.bootstrapSession();

    expect(organizationService.refreshOrganizations).toHaveBeenCalledTimes(1);

    refreshSubject.next([{ id: 'org-1', type: 'school', role: 'teacher' }]);
    refreshSubject.complete();

    await Promise.all([bootstrapOne, bootstrapTwo]);

    expect(organizationService.refreshOrganizations).toHaveBeenCalledTimes(1);
  });

  it('does not infer active role from organizations[0] when active_org_id points elsewhere', async () => {
    organizationService.activeOrgId = 'org-2';
    organizationService.activeOrgRole = null;
    organizationService.setOrganizations([
      { id: 'org-1', type: 'school', role: 'teacher' },
      { id: 'org-2', type: 'school', role: 'org_admin' },
    ]);
    authService.payload = {
      sub: 'student',
      user_id: 'user-1',
      fullname: 'Student User',
      role: 'student',
      exp: Math.floor(Date.now() / 1000) + 3600,
    };

    await service.bootstrapSession();

    const outcome = service.getCurrentOutcome();
    expect(outcome.activeOrgRole).toBe('org_admin');
    expect(service.hasAnyRole('org_admin')).toBeTrue();
    expect(service.hasAnyRole('teacher')).toBeFalse();
  });
});
