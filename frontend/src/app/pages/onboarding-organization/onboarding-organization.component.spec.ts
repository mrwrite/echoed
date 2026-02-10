import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { OnboardingOrganizationComponent } from './onboarding-organization.component';
import { OrganizationService } from '../../services/organization.service';
import { MetaService } from '../../services/meta.service';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';

class MockOrganizationService {
  createOrganization() {
    return of({ id: 'org-1', name: 'Test Org', type: 'school' });
  }
  refreshOrganizations() {
    return of([]);
  }
  setActiveOrg() {
    return of({ access_token: 'token', token_type: 'bearer' });
  }
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

class MockRouter {
  navigate() {
    return Promise.resolve(true);
  }
}

describe('OnboardingOrganizationComponent', () => {
  let fixture: ComponentFixture<OnboardingOrganizationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OnboardingOrganizationComponent],
      providers: [
        { provide: OrganizationService, useClass: MockOrganizationService },
        { provide: MetaService, useClass: MockMetaService },
        { provide: AuthService, useClass: MockAuthService },
        { provide: Router, useClass: MockRouter },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(OnboardingOrganizationComponent);
  });

  it('renders onboarding header', () => {
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h1')?.textContent).toContain('Create your organization');
  });
});
