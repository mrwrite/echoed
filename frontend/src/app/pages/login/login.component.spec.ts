import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { of } from 'rxjs';
import { Router } from '@angular/router';
import { LoginComponent } from './login.component';
import { AuthService } from '../../services/auth.service';
import { OrganizationService } from '../../services/organization.service';
import { PermissionsService } from '../../services/permissions.service';

class MockAuthService {
  role = 'teacher';

  login() {
    return of({ access_token: 'token' });
  }

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
  refreshOrganizations() {
    return of([{ id: 'org-1', type: 'school', role: 'teacher' }]);
  }
}

describe('LoginComponent', () => {
  let component: LoginComponent;
  let fixture: ComponentFixture<LoginComponent>;
  let router: jasmine.SpyObj<Router>;
  let permissionsService: jasmine.SpyObj<PermissionsService>;
  let authService: MockAuthService;

  beforeEach(async () => {
    router = jasmine.createSpyObj<Router>('Router', ['navigateByUrl']);
    router.navigateByUrl.and.resolveTo(true);

    permissionsService = jasmine.createSpyObj<PermissionsService>('PermissionsService', ['bootstrapSession']);

    TestBed.overrideComponent(LoginComponent, {
      set: {
        template: '',
      },
    });

    await TestBed.configureTestingModule({
      imports: [LoginComponent],
      providers: [
        { provide: Router, useValue: router },
        { provide: AuthService, useClass: MockAuthService },
        { provide: OrganizationService, useClass: MockOrganizationService },
        { provide: PermissionsService, useValue: permissionsService },
      ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;
    authService = TestBed.inject(AuthService) as unknown as MockAuthService;
    sessionStorage.clear();
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('awaits session bootstrap before navigating to dashboard', fakeAsync(() => {
    let resolveBootstrap: () => void = () => {};
    permissionsService.bootstrapSession.and.returnValue(new Promise<void>((resolve) => {
      resolveBootstrap = resolve;
    }));

    component.login(new Event('submit'));
    tick();

    expect(permissionsService.bootstrapSession).toHaveBeenCalled();
    expect(router.navigateByUrl).not.toHaveBeenCalledWith('/home');

    resolveBootstrap();
    tick();

    expect(router.navigateByUrl).toHaveBeenCalledWith('/home');
  }));

  it('routes super admin to dashboard instead of onboarding when org list is empty', fakeAsync(() => {
    authService.role = 'super_admin';
    spyOn(TestBed.inject(OrganizationService), 'refreshOrganizations').and.returnValue(of([]));
    permissionsService.bootstrapSession.and.resolveTo();

    component.login(new Event('submit'));
    tick();

    expect(router.navigateByUrl).toHaveBeenCalledWith('/home');
    expect(router.navigateByUrl).not.toHaveBeenCalledWith('/onboarding/organization');
  }));

  it('routes users with pending registration setup to onboarding before home', fakeAsync(() => {
    permissionsService.bootstrapSession.and.resolveTo();
    sessionStorage.setItem('pending_org_creation', JSON.stringify({ name: 'Bright Futures', type: 'school' }));

    component.login(new Event('submit'));
    tick();

    expect(router.navigateByUrl).toHaveBeenCalledWith('/onboarding/organization');
    expect(router.navigateByUrl).not.toHaveBeenCalledWith('/home');
  }));

  it('routes users with only personal organizations to onboarding', fakeAsync(() => {
    permissionsService.bootstrapSession.and.resolveTo();
    spyOn(TestBed.inject(OrganizationService), 'refreshOrganizations').and.returnValue(
      of([{ id: 'personal-1', name: 'Personal Workspace', type: 'personal', role: 'teacher' }])
    );

    component.login(new Event('submit'));
    tick();

    expect(router.navigateByUrl).toHaveBeenCalledWith('/onboarding/organization');
  }));
});
