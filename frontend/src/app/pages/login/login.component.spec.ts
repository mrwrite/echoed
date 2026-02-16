import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { of } from 'rxjs';
import { Router } from '@angular/router';
import { LoginComponent } from './login.component';
import { AuthService } from '../../services/auth.service';
import { OrganizationService } from '../../services/organization.service';
import { PermissionsService } from '../../services/permissions.service';

class MockAuthService {
  login() {
    return of({ access_token: 'token' });
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

  beforeEach(async () => {
    router = jasmine.createSpyObj<Router>('Router', ['navigate']);
    router.navigate.and.resolveTo(true);

    permissionsService = jasmine.createSpyObj<PermissionsService>('PermissionsService', ['bootstrapSession']);

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
    expect(router.navigate).not.toHaveBeenCalledWith(['/home']);

    resolveBootstrap();
    tick();

    expect(router.navigate).toHaveBeenCalledWith(['/home']);
  }));
});
