import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { of } from 'rxjs';
import { OnboardingOrganizationComponent } from './onboarding-organization.component';
import { OrganizationService } from '../../services/organization.service';
import { MetaService } from '../../services/meta.service';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';
import { PermissionsService } from '../../services/permissions.service';

class MockOrganizationService {
  createOrganization = jasmine.createSpy('createOrganization').and.returnValue(
    of({ id: 'org-1', name: 'Test Org', type: 'school' })
  );
  refreshOrganizations = jasmine.createSpy('refreshOrganizations').and.returnValue(of([]));
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

    fixture = TestBed.createComponent(OnboardingOrganizationComponent);
    component = fixture.componentInstance;
    orgService = TestBed.inject(OrganizationService) as unknown as MockOrganizationService;
    fixture.detectChanges();
  });

  it('renders onboarding header', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h1')?.textContent).toContain('Create your organization');
  });

  it('creates org once, sets active org context, refreshes permissions, and navigates home', fakeAsync(() => {
    component.organizationName = 'Test Org';
    component.organizationType = 'school';

    component.onSubmit(new Event('submit'));
    tick();

    expect(orgService.createOrganization).toHaveBeenCalledTimes(1);
    expect(orgService.setActiveOrg).toHaveBeenCalledWith('org-1', 'org_admin');
    expect(permissionsService.refreshSession).toHaveBeenCalled();
    expect(router.navigateByUrl).toHaveBeenCalledWith('/home');
  }));

  it('prevents native form submission reload on submit', () => {
    component.organizationName = 'Test Org';
    component.organizationType = 'school';

    const event = new Event('submit');
    spyOn(event, 'preventDefault');

    component.onSubmit(event);

    expect(event.preventDefault).toHaveBeenCalled();
  });
});
