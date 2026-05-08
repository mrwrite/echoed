import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { of } from 'rxjs';
import { Router } from '@angular/router';
import { LoginComponent } from './login.component';
import { AuthService } from '../../services/auth.service';
import { PermissionsService } from '../../services/permissions.service';
import { BootstrapOutcome } from '../../services/permissions.service';

class MockAuthService {
  login() {
    return of({ access_token: 'token' });
  }
}

describe('LoginComponent', () => {
  let component: LoginComponent;
  let fixture: ComponentFixture<LoginComponent>;
  let router: jasmine.SpyObj<Router>;
  let permissionsService: jasmine.SpyObj<PermissionsService>;

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

  beforeEach(async () => {
    router = jasmine.createSpyObj<Router>('Router', ['navigateByUrl']);
    router.navigateByUrl.and.resolveTo(true);

    permissionsService = jasmine.createSpyObj<PermissionsService>('PermissionsService', ['bootstrapSession', 'getCurrentOutcome']);
    permissionsService.getCurrentOutcome.and.returnValue(readyOutcome);

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
        { provide: PermissionsService, useValue: permissionsService },
      ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;
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

  it('routes login to home when bootstrap outcome is ready', fakeAsync(() => {
    permissionsService.bootstrapSession.and.resolveTo();
    permissionsService.getCurrentOutcome.and.returnValue(readyOutcome);

    component.login(new Event('submit'));
    tick();

    expect(router.navigateByUrl).toHaveBeenCalledWith('/home');
    expect(router.navigateByUrl).not.toHaveBeenCalledWith('/onboarding/organization');
  }));

  it('routes login to onboarding when bootstrap outcome is onboardingRequired', fakeAsync(() => {
    permissionsService.bootstrapSession.and.resolveTo();
    permissionsService.getCurrentOutcome.and.returnValue({
      ...readyOutcome,
      status: 'onboardingRequired',
      onboardingRequired: true,
    });

    component.login(new Event('submit'));
    tick();

    expect(router.navigateByUrl).toHaveBeenCalledWith('/onboarding/organization');
    expect(router.navigateByUrl).not.toHaveBeenCalledWith('/home');
  }));

  it('handles failed bootstrap without navigating to home', fakeAsync(() => {
    permissionsService.bootstrapSession.and.resolveTo();
    permissionsService.getCurrentOutcome.and.returnValue({
      ...readyOutcome,
      status: 'failed',
      ready: false,
      failed: true,
      error: 'org_hydration_failed',
    });

    component.login(new Event('submit'));
    tick();

    expect(router.navigateByUrl).not.toHaveBeenCalledWith('/home');
    expect(component.errorMessage).toContain('Unable to complete session bootstrap');
  }));

  it('keeps super-admin-equivalent ready outcomes on the home route', fakeAsync(() => {
    permissionsService.bootstrapSession.and.resolveTo();
    permissionsService.getCurrentOutcome.and.returnValue({
      ...readyOutcome,
      activeOrgId: null,
      activeOrgRole: null,
      organizations: [],
    });

    component.login(new Event('submit'));
    tick();

    expect(router.navigateByUrl).toHaveBeenCalledWith('/home');
  }));
});
