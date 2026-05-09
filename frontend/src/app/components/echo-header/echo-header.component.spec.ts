import { Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BehaviorSubject, Subject, of, throwError } from 'rxjs';

import { EchoHeaderComponent } from './echo-header.component';
import { AuthService } from '../../services/auth.service';
import { OrganizationService } from '../../services/organization.service';
import { PermissionsService } from '../../services/permissions.service';

class MockAuthService {
  logout = jasmine.createSpy('logout');
}

class MockOrganizationService {
  private readonly activeOrgSubject = new BehaviorSubject<string | null>(null);
  private readonly organizationsSubject = new BehaviorSubject<any[]>([]);
  activeOrg$ = this.activeOrgSubject.asObservable();
  organizations$ = this.organizationsSubject.asObservable();
  refreshOrganizationsResponse = of([]);
  refreshOrganizations = jasmine.createSpy('refreshOrganizations').and.callFake(() => this.refreshOrganizationsResponse);
  setActiveOrg = jasmine.createSpy('setActiveOrg').and.returnValue(of({
    access_token: 'new-token',
    token_type: 'bearer',
    active_org_id: 'org-2',
    active_org_role: 'content_admin',
    active_organization: { id: 'org-2', name: 'Confirmed Org', type: 'school', role: 'content_admin' },
  }));
  clearActiveOrg = jasmine.createSpy('clearActiveOrg');
  currentActiveOrgId: string | null = null;

  emitOrganizations(orgs: any[]) {
    this.organizationsSubject.next(orgs);
  }

  emitActiveOrg(orgId: string | null) {
    this.currentActiveOrgId = orgId;
    this.activeOrgSubject.next(orgId);
  }

  getActiveOrgId() {
    return this.currentActiveOrgId;
  }
}

class MockPermissionsService {
  readonly ready$ = new BehaviorSubject<boolean>(true);
  resetSession = jasmine.createSpy('resetSession');
  bootstrapSession = jasmine.createSpy('bootstrapSession').and.resolveTo();
}

describe('EchoHeaderComponent', () => {
  let component: EchoHeaderComponent;
  let fixture: ComponentFixture<EchoHeaderComponent>;
  let authService: MockAuthService;
  let organizationService: MockOrganizationService;
  let permissionsService: MockPermissionsService;
  let router: Router;

  async function createComponent() {
    await TestBed.configureTestingModule({
      imports: [RouterTestingModule, EchoHeaderComponent],
      providers: [
        { provide: AuthService, useClass: MockAuthService },
        { provide: OrganizationService, useClass: MockOrganizationService },
        { provide: PermissionsService, useClass: MockPermissionsService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(EchoHeaderComponent);
    component = fixture.componentInstance;
    component.userinfo = { fullname: 'Teacher User', role: 'teacher' } as any;
    authService = TestBed.inject(AuthService) as unknown as MockAuthService;
    organizationService = TestBed.inject(OrganizationService) as unknown as MockOrganizationService;
    permissionsService = TestBed.inject(PermissionsService) as unknown as MockPermissionsService;
    router = TestBed.inject(Router);
  }

  beforeEach(async () => {
    await createComponent();
  });

  it('shows org-loading state while organizations load', () => {
    const pendingRefresh = new Subject<any>();
    organizationService.refreshOrganizationsResponse = pendingRefresh.asObservable();

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('[data-echo-loading="compact"]')).not.toBeNull();
    expect(compiled.textContent).toContain('Loading organizations');
  });

  it('shows empty state when no organizations are available', () => {
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('[data-echo-state="empty"]')).not.toBeNull();
    expect(compiled.textContent).toContain('No organizations are available');
  });

  it('switch pending disables duplicate switching', () => {
    const pendingSwitch = new Subject<any>();
    organizationService.setActiveOrg.and.returnValue(pendingSwitch.asObservable());
    organizationService.emitActiveOrg('org-1');
    organizationService.emitOrganizations([
      { id: 'org-1', name: 'Org One', type: 'school', role: 'teacher' },
      { id: 'org-2', name: 'Org Two', type: 'school', role: 'content_admin' },
    ]);

    fixture.detectChanges();
    component.switchOrg('org-2');
    component.switchOrg('org-2');
    fixture.detectChanges();

    expect(component.switchPending).toBeTrue();
    expect(organizationService.setActiveOrg).toHaveBeenCalledTimes(1);
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Switching organization');
  });

  it('switch failure preserves confirmed active org', () => {
    organizationService.setActiveOrg.and.returnValue(
      throwError(() => new Error('switch failed')),
    );
    organizationService.emitActiveOrg('org-1');
    organizationService.emitOrganizations([
      { id: 'org-1', name: 'Org One', type: 'school', role: 'teacher' },
      { id: 'org-2', name: 'Org Two', type: 'school', role: 'content_admin' },
    ]);

    fixture.detectChanges();
    component.switchOrg('org-2');
    fixture.detectChanges();

    expect(component.activeOrgId).toBe('org-1');
    expect(component.activeOrganizationName).toBe('Org One');
    expect(component.switchError).toContain('has not changed');
    expect(permissionsService.resetSession).not.toHaveBeenCalled();
    expect(permissionsService.bootstrapSession).not.toHaveBeenCalled();
  });

  it('switch success updates confirmed active org display', async () => {
    const switchSubject = new Subject<any>();
    organizationService.setActiveOrg.and.returnValue(switchSubject.asObservable());
    organizationService.emitActiveOrg('org-1');
    organizationService.emitOrganizations([
      { id: 'org-1', name: 'Org One', type: 'school', role: 'teacher' },
      { id: 'org-2', name: 'Org Two', type: 'school', role: 'content_admin' },
    ]);

    fixture.detectChanges();
    component.switchOrg('org-2');
    organizationService.emitActiveOrg('org-2');
    switchSubject.next({
      access_token: 'new-token',
      token_type: 'bearer',
      active_org_id: 'org-2',
      active_org_role: 'content_admin',
    });
    switchSubject.complete();
    await Promise.resolve();
    fixture.detectChanges();

    expect(component.activeOrgId).toBe('org-2');
    expect(component.activeOrganizationName).toBe('Org Two');
    expect(component.switchSuccess).toContain('Org Two');
  });

  it('does not auto-select organizations[0] when no active org exists', () => {
    organizationService.emitOrganizations([
      { id: 'org-1', name: 'Org One', type: 'school', role: 'teacher' },
    ]);

    fixture.detectChanges();

    expect(organizationService.setActiveOrg).not.toHaveBeenCalled();
  });

  it('preserves existing logout and navigation behavior', () => {
    spyOn(router, 'navigate');
    fixture.detectChanges();

    component.logout();

    expect(authService.logout).toHaveBeenCalled();
    expect(organizationService.clearActiveOrg).toHaveBeenCalled();
    expect(permissionsService.resetSession).toHaveBeenCalled();
    expect(router.navigate).toHaveBeenCalledWith(['/login']);
  });

  it('keeps important header controls labeled for accessibility', () => {
    organizationService.emitOrganizations([
      { id: 'org-1', name: 'Org One', type: 'school', role: 'teacher' },
    ]);

    fixture.detectChanges();

    const buttons = Array.from(fixture.nativeElement.querySelectorAll('button')) as HTMLButtonElement[];
    const helpButton = buttons.find((button) => button.textContent?.includes('Help & Support')) as HTMLButtonElement;
    const guidedTourButton = buttons.find((button) => button.textContent?.includes('Start Guided Tour')) as HTMLButtonElement;
    const profileButton = buttons.find((button) => button.getAttribute('aria-label') === 'Open profile menu') as HTMLButtonElement;

    expect(helpButton.getAttribute('aria-label')).toBe('Open help and support');
    expect(guidedTourButton.getAttribute('aria-label')).toBe('Start guided tour');
    expect(profileButton).not.toBeNull();
  });
});
