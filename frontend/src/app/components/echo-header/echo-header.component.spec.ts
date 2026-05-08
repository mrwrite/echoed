import { RouterTestingModule } from '@angular/router/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BehaviorSubject, Observable, Subject, of, throwError } from 'rxjs';

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
  refreshOrganizations = jasmine.createSpy('refreshOrganizations').and.returnValue(of([]));
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
  let organizationService: MockOrganizationService;
  let permissionsService: MockPermissionsService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RouterTestingModule, EchoHeaderComponent],
      providers: [
        { provide: AuthService, useClass: MockAuthService },
        { provide: OrganizationService, useClass: MockOrganizationService },
        { provide: PermissionsService, useClass: MockPermissionsService },
      ],
    })
    .compileComponents();

    fixture = TestBed.createComponent(EchoHeaderComponent);
    component = fixture.componentInstance;
    component.userinfo = { fullname: 'Teacher User', role: 'teacher' } as any;
    organizationService = TestBed.inject(OrganizationService) as unknown as MockOrganizationService;
    permissionsService = TestBed.inject(PermissionsService) as unknown as MockPermissionsService;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('renders confirmed org selector state after readiness', () => {
    organizationService.emitActiveOrg('org-2');
    organizationService.emitOrganizations([
      { id: 'org-1', name: 'Org One', type: 'school', role: 'teacher' },
      { id: 'org-2', name: 'Org Two', type: 'school', role: 'content_admin' },
    ]);
    fixture.detectChanges();

    expect(component.activeOrgId).toBe('org-2');
  });

  it('does not auto-select organizations[0] when no active org exists', () => {
    organizationService.emitOrganizations([
      { id: 'org-1', name: 'Org One', type: 'school', role: 'teacher' },
    ]);

    expect(organizationService.setActiveOrg).not.toHaveBeenCalled();
  });

  it('uses confirmed active org when present', () => {
    organizationService.emitActiveOrg('org-2');
    organizationService.emitOrganizations([
      { id: 'org-1', name: 'Org One', type: 'school', role: 'teacher' },
      { id: 'org-2', name: 'Org Two', type: 'school', role: 'content_admin' },
    ]);

    expect(component.activeOrgId).toBe('org-2');
  });

  it('refreshes permissions only after confirmed switch success', async () => {
    const switchSubject = new Subject<any>();
    organizationService.setActiveOrg.and.returnValue(switchSubject.asObservable());
    organizationService.emitActiveOrg('org-1');
    organizationService.emitOrganizations([
      { id: 'org-1', name: 'Org One', type: 'school', role: 'teacher' },
      { id: 'org-2', name: 'Org Two', type: 'school', role: 'content_admin' },
    ]);

    component.switchOrg('org-2');

    expect(permissionsService.resetSession).not.toHaveBeenCalled();
    expect(permissionsService.bootstrapSession).not.toHaveBeenCalled();

    organizationService.emitActiveOrg('org-2');
    switchSubject.next({
      access_token: 'new-token',
      token_type: 'bearer',
      active_org_id: 'org-2',
      active_org_role: 'content_admin',
    });
    switchSubject.complete();
    await Promise.resolve();

    expect(permissionsService.resetSession).toHaveBeenCalled();
    expect(permissionsService.bootstrapSession).toHaveBeenCalled();
    expect(component.activeOrgId).toBe('org-2');
  });

  it('does not refresh permissions when switch fails', () => {
    organizationService.setActiveOrg.and.returnValue(
      throwError(() => new Error('switch failed')),
    );

    component.switchOrg('org-2');

    expect(permissionsService.resetSession).not.toHaveBeenCalled();
    expect(permissionsService.bootstrapSession).not.toHaveBeenCalled();
  });
});
