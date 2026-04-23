import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { of, throwError } from 'rxjs';
import { OnboardingOrganizationComponent } from './onboarding-organization.component';
import { OrganizationService } from '../../services/organization.service';
import { MetaService } from '../../services/meta.service';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';
import { PermissionsService } from '../../services/permissions.service';
import { PENDING_ORG_CREATION_KEY } from '../../shared/onboarding-flow';

class MockOrganizationService {
  createOrganization = jasmine.createSpy('createOrganization').and.returnValue(
    of({ id: 'org-1', name: 'Test Org', type: 'school' })
  );
  refreshOrganizations = jasmine.createSpy('refreshOrganizations').and.returnValue(
    of([{ id: 'org-1', name: 'Test Org', type: 'school', role: 'org_admin' }])
  );
  setActiveOrg = jasmine.createSpy('setActiveOrg').and.returnValue(
    of({ access_token: 'token', token_type: 'bearer' })
  );
}

class MockMetaService {
  getEnums() {
    return of({
      organizationRoles: [],
      organizationTypes: [{ key: 'SCHOOL', value: 'school', label: 'School' }],
    });
  }
}

class MockAuthService {
  getToken() {
    return 'token';
  }
  getTokenPayload() {
    return { role: 'teacher' };
  }
}

describe('OnboardingOrganizationComponent', () => {
  let fixture: ComponentFixture<OnboardingOrganizationComponent>;
  let component: OnboardingOrganizationComponent;
  let orgService: MockOrganizationService;
  let router: jasmine.SpyObj<Router>;
  let permissionsService: jasmine.SpyObj<PermissionsService>;

  beforeEach(async () => {
    router = jasmine.createSpyObj<Router>('Router', ['navigateByUrl']);
    router.navigateByUrl.and.resolveTo(true);
    permissionsService = jasmine.createSpyObj<PermissionsService>('PermissionsService', ['refreshSession']);
    permissionsService.refreshSession.and.resolveTo();

    await TestBed.configureTestingModule({
      imports: [OnboardingOrganizationComponent],
      providers: [
        { provide: OrganizationService, useClass: MockOrganizationService },
        { provide: MetaService, useClass: MockMetaService },
        { provide: AuthService, useClass: MockAuthService },
        { provide: PermissionsService, useValue: permissionsService },
        { provide: Router, useValue: router },
      ],
    }).compileComponents();

    sessionStorage.clear();
    fixture = TestBed.createComponent(OnboardingOrganizationComponent);
    component = fixture.componentInstance;
    orgService = TestBed.inject(OrganizationService) as unknown as MockOrganizationService;
  });

  it('renders onboarding header', () => {
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h1')?.textContent).toContain('Create your organization');
  });

  it('prefills saved registration intent when onboarding loads', () => {
    sessionStorage.setItem(PENDING_ORG_CREATION_KEY, JSON.stringify({ name: 'Bright Futures', type: 'school' }));

    fixture.detectChanges();

    expect(component.organizationName).toBe('Bright Futures');
    expect(component.organizationType).toBe('school');
  });

  it('creates org, sets active org context, refreshes permissions, clears pending setup, and navigates home', fakeAsync(() => {
    sessionStorage.setItem(PENDING_ORG_CREATION_KEY, JSON.stringify({ name: 'Test Org', type: 'school' }));
    fixture.detectChanges();

    component.onSubmit(new Event('submit'));
    tick();

    expect(orgService.createOrganization).toHaveBeenCalledTimes(1);
    expect(orgService.setActiveOrg).toHaveBeenCalledWith('org-1', 'org_admin');
    expect(permissionsService.refreshSession).toHaveBeenCalled();
    expect(sessionStorage.getItem(PENDING_ORG_CREATION_KEY)).toBeNull();
    expect(router.navigateByUrl).toHaveBeenCalledWith('/home');
  }));

  it('preserves entered values and pending setup when organization creation fails', fakeAsync(() => {
    orgService.createOrganization.and.returnValue(
      throwError(() => ({ error: { detail: 'Creation failed.' } }))
    );

    fixture.detectChanges();
    component.organizationName = 'Retry Org';
    component.organizationType = 'school';
    sessionStorage.setItem(PENDING_ORG_CREATION_KEY, JSON.stringify({ name: 'Retry Org', type: 'school' }));

    component.onSubmit(new Event('submit'));
    tick();

    expect(component.organizationName).toBe('Retry Org');
    expect(component.errorMessage).toBe('Creation failed.');
    expect(sessionStorage.getItem(PENDING_ORG_CREATION_KEY)).not.toBeNull();
    expect(router.navigateByUrl).not.toHaveBeenCalled();
  }));
});
