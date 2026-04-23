import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { of } from 'rxjs';

import { RegistrationComponent } from './registration.component';
import { AuthService } from '../../services/auth.service';
import { MetaService } from '../../services/meta.service';
import { PENDING_ORG_CREATION_KEY } from '../../shared/onboarding-flow';

class MockAuthService {
  register = jasmine.createSpy('register').and.returnValue(of({}));
}

class MockMetaService {
  getEnums = jasmine.createSpy('getEnums').and.returnValue(of({
    organizationRoles: [
      { key: 'TEACHER', value: 'teacher', label: 'Teacher' },
      { key: 'STUDENT', value: 'student', label: 'Student' },
    ],
    organizationTypes: [
      { key: 'SCHOOL', value: 'school', label: 'School' },
      { key: 'FAMILY', value: 'family', label: 'Family' },
    ],
  }));
}

describe('RegistrationComponent', () => {
  let component: RegistrationComponent;
  let fixture: ComponentFixture<RegistrationComponent>;
  let authService: MockAuthService;
  let router: jasmine.SpyObj<Router>;

  beforeEach(async () => {
    router = jasmine.createSpyObj<Router>('Router', ['navigate']);
    router.navigate.and.resolveTo(true);

    TestBed.overrideComponent(RegistrationComponent, {
      set: {
        template: '',
      },
    });

    await TestBed.configureTestingModule({
      imports: [RegistrationComponent],
      providers: [
        { provide: Router, useValue: router },
        { provide: AuthService, useClass: MockAuthService },
        { provide: MetaService, useClass: MockMetaService },
      ],
    }).compileComponents();

    sessionStorage.clear();
    fixture = TestBed.createComponent(RegistrationComponent);
    component = fixture.componentInstance;
    authService = TestBed.inject(AuthService) as unknown as MockAuthService;
    fixture.detectChanges();
  });

  function fillBaseForm(): void {
    component.registrationForm.patchValue({
      email: 'teacher@example.com',
      firstName: 'Ada',
      lastName: 'Lovelace',
      role: 'teacher',
      password: 'secret123',
      confirmPassword: 'secret123',
    });
  }

  it('stores normalized pending org setup when registration includes organization creation', () => {
    fillBaseForm();
    component.registrationForm.patchValue({
      createOrganization: true,
      organizationName: '  Bright Futures Academy  ',
    });

    component.onSubmit();

    expect(authService.register).toHaveBeenCalled();
    expect(sessionStorage.getItem(PENDING_ORG_CREATION_KEY)).toBe(
      JSON.stringify({ name: 'Bright Futures Academy', type: 'school' }),
    );
    expect(router.navigate).toHaveBeenCalledWith(['/login']);
  });

  it('clears pending org setup when registration skips organization creation', () => {
    fillBaseForm();
    sessionStorage.setItem(PENDING_ORG_CREATION_KEY, JSON.stringify({ name: 'Old Org', type: 'school' }));

    component.onSubmit();

    expect(sessionStorage.getItem(PENDING_ORG_CREATION_KEY)).toBeNull();
  });

  it('shows the setup continuation copy when organization creation is selected', () => {
    component.registrationForm.patchValue({ createOrganization: true });

    expect(component.organizationSetupSummary).toContain('directly into organization setup');
    expect(component.submitLabel).toContain('continue to setup');
  });
});
