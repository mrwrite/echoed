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
  activeOrg$ = of(null);
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
    component.compactShell = false;
    component.sidebarCollapsed = false;
    fixture.detectChanges();

    const shell = fixture.nativeElement.querySelector('.home-shell') as HTMLElement;

    expect(shell.style.getPropertyValue('--echo-shell-sidebar-width')).toBe('var(--echo-sidebar-expanded-width)');
  });

  it('updates shell width when the sidebar is collapsed', () => {
    component.sidebarCollapsed = true;
    fixture.detectChanges();

    const shell = fixture.nativeElement.querySelector('.home-shell') as HTMLElement;
    expect(shell.style.getPropertyValue('--echo-shell-sidebar-width')).toBe('var(--echo-sidebar-collapsed-width)');
  });

  it('does not duplicate bootstrap when guard/session is already ready', () => {
    const permissionsService = TestBed.inject(PermissionsService) as unknown as MockPermissionsService;

    expect(permissionsService.bootstrapSession).not.toHaveBeenCalled();
  });

  it('renders a loading shell before readiness', () => {
    const permissionsService = TestBed.inject(PermissionsService) as unknown as MockPermissionsService;
    permissionsService.ready$.next(false);
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('[aria-label="shell-loading"]')).not.toBeNull();
    expect(fixture.nativeElement.querySelector('echo-header')).toBeNull();
    expect(fixture.nativeElement.querySelector('echo-sidebar')).toBeNull();
  });

  it('exposes skip navigation and a focusable main landmark', () => {
    const skipLink = fixture.nativeElement.querySelector('.skip-link') as HTMLAnchorElement;
    const main = fixture.nativeElement.querySelector('main') as HTMLElement;

    expect(skipLink.getAttribute('href')).toBe('#echoed-main-content');
    expect(main.getAttribute('id')).toBe('echoed-main-content');
    expect(main.getAttribute('tabindex')).toBe('-1');
  });

  it('preserves lesson-mode shell behavior after readiness', () => {
    component.lessonMode = true;
    fixture.detectChanges();

    const shell = fixture.nativeElement.querySelector('.home-shell') as HTMLElement;
    expect(shell.classList).toContain('home-shell--lesson');
    expect(shell.style.getPropertyValue('--echo-shell-sidebar-width')).toBe('0px');
  });

  it('collapses the sidebar by default on compact viewports', () => {
    component.compactShell = true;
    component.sidebarCollapsed = true;
    fixture.detectChanges();

    expect(component.compactShell).toBeTrue();
    expect(component.sidebarCollapsed).toBeTrue();
    expect(component.sidebarWidth).toBe('var(--echo-sidebar-collapsed-width)');
  });

  it('keeps shell width stable when compact navigation expands as an overlay', () => {
    component.compactShell = true;
    component.openMobileNavigation();
    fixture.detectChanges();

    const shell = fixture.nativeElement.querySelector('.home-shell') as HTMLElement;
    const sidebar = fixture.nativeElement.querySelector('echo-sidebar') as HTMLElement;
    expect(component.sidebarOverlayMode).toBeTrue();
    expect(shell.style.getPropertyValue('--echo-shell-sidebar-width')).toBe('var(--echo-sidebar-collapsed-width)');
    expect(sidebar.classList).toContain('home-shell__sidebar--overlay');
  });

  it('opens and closes mobile navigation with Escape', () => {
    component.compactShell = true;
    fixture.detectChanges();

    component.openMobileNavigation();
    fixture.detectChanges();
    expect(component.mobileNavigationOpen).toBeTrue();
    expect(document.body.classList).toContain('echo-mobile-nav-open');

    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
    fixture.detectChanges();

    expect(component.mobileNavigationOpen).toBeFalse();
    expect(document.body.classList).not.toContain('echo-mobile-nav-open');
  });

  it('returns focus to the mobile trigger when navigation closes', async () => {
    component.compactShell = true;
    fixture.detectChanges();

    const trigger = fixture.nativeElement.querySelector('.mobile-nav-trigger') as HTMLButtonElement;
    trigger.focus();
    trigger.click();
    fixture.detectChanges();

    component.closeMobileNavigation(true);
    await fixture.whenStable();
    fixture.detectChanges();

    expect(document.activeElement).toBe(trigger);
  });
});
