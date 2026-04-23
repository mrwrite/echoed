import { ComponentFixture, TestBed } from '@angular/core/testing';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { RouterTestingModule } from '@angular/router/testing';
import { BehaviorSubject, of } from 'rxjs';

import { HomeComponent } from './home.component';
import { PermissionsService } from '../../services/permissions.service';
import { DemoTourService } from '../../services/demo-tour.service';
import { AuthService } from '../../services/auth.service';
import { OrganizationService } from '../../services/organization.service';

class MockPermissionsService {
  readonly user$ = new BehaviorSubject<any>({ fullname: 'Test User', role: 'content_admin' });
  readonly permissions$ = new BehaviorSubject<Set<string>>(new Set(['nav:dashboard', 'nav:courses']));
  readonly ready$ = new BehaviorSubject<boolean>(true);

  bootstrapSession = jasmine.createSpy('bootstrapSession').and.resolveTo();
  resetSession = jasmine.createSpy('resetSession');
}

class MockDemoTourService {
  startTour = jasmine.createSpy('startTour');
}

class MockAuthService {
  logout = jasmine.createSpy('logout');
}

class MockOrganizationService {
  organizations$ = of([]);
  refreshOrganizations = jasmine.createSpy('refreshOrganizations').and.returnValue(of([]));
  getActiveOrgId = jasmine.createSpy('getActiveOrgId').and.returnValue(null);
  setActiveOrg = jasmine.createSpy('setActiveOrg').and.returnValue(of({ access_token: 'token', token_type: 'bearer' }));
  clearActiveOrg = jasmine.createSpy('clearActiveOrg');
}

describe('HomeComponent', () => {
  let component: HomeComponent;
  let fixture: ComponentFixture<HomeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RouterTestingModule, NoopAnimationsModule, HomeComponent],
      providers: [
        { provide: PermissionsService, useClass: MockPermissionsService },
        { provide: DemoTourService, useClass: MockDemoTourService },
        { provide: AuthService, useClass: MockAuthService },
        { provide: OrganizationService, useClass: MockOrganizationService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(HomeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('binds shell width to the expanded sidebar by default', () => {
    const shell = fixture.nativeElement.querySelector('.home-shell') as HTMLElement;

    expect(shell.style.getPropertyValue('--echo-shell-sidebar-width')).toBe('var(--echo-sidebar-expanded-width)');
  });

  it('updates shell width when the sidebar is collapsed', () => {
    component.sidebarCollapsed = true;
    fixture.detectChanges();

    const shell = fixture.nativeElement.querySelector('.home-shell') as HTMLElement;
    expect(shell.style.getPropertyValue('--echo-shell-sidebar-width')).toBe('var(--echo-sidebar-collapsed-width)');
  });
});
