import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { OrganizationService } from './organization.service';
import { AuthService } from './auth.service';
import { environment } from '../../environments/environment';

describe('OrganizationService', () => {
  let service: OrganizationService;
  let httpMock: HttpTestingController;
  let authService: jasmine.SpyObj<AuthService>;
  let activeOrgValues: Array<string | null>;

  beforeEach(() => {
    authService = jasmine.createSpyObj<AuthService>('AuthService', ['applyTokenResponse']);

    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        OrganizationService,
        { provide: AuthService, useValue: authService },
      ],
    });

    localStorage.clear();
    service = TestBed.inject(OrganizationService);
    httpMock = TestBed.inject(HttpTestingController);
    activeOrgValues = [];
    service.activeOrg$.subscribe((value) => activeOrgValues.push(value));
  });

  afterEach(() => {
    httpMock.verify();
    localStorage.clear();
  });

  it('updates token, active org id, active org role, and active org subject only after switch success', () => {
    authService.applyTokenResponse.and.callFake((response) => {
      localStorage.setItem('auth_token', response.access_token);
      if (response.active_org_id) {
        localStorage.setItem('active_org_id', response.active_org_id);
      }
      if (response.active_org_role) {
        localStorage.setItem('active_org_role', response.active_org_role);
      }
    });

    service.setActiveOrg('org-2').subscribe();

    const request = httpMock.expectOne(`${environment.apiUrl}/api/orgs/org-2/switch`);
    expect(localStorage.getItem('auth_token')).toBeNull();
    expect(localStorage.getItem('active_org_id')).toBeNull();
    expect(localStorage.getItem('active_org_role')).toBeNull();
    expect(activeOrgValues.at(-1)).toBeNull();

    request.flush({
      access_token: 'new-token',
      token_type: 'bearer',
      active_org_id: 'org-2',
      active_org_role: 'content_admin',
      active_organization: {
        id: 'org-2',
        name: 'Confirmed Org',
        type: 'school',
        role: 'content_admin',
      },
    });

    expect(authService.applyTokenResponse).toHaveBeenCalled();
    expect(localStorage.getItem('auth_token')).toBe('new-token');
    expect(localStorage.getItem('active_org_id')).toBe('org-2');
    expect(localStorage.getItem('active_org_role')).toBe('content_admin');
    expect(activeOrgValues.at(-1)).toBe('org-2');
  });

  it('preserves previous state when switch fails', () => {
    localStorage.setItem('auth_token', 'old-token');
    localStorage.setItem('active_org_id', 'org-1');
    localStorage.setItem('active_org_role', 'teacher');
    (service as any).activeOrgSubject.next('org-1');

    service.setActiveOrg('org-2').subscribe({
      error: () => undefined,
    });

    const request = httpMock.expectOne(`${environment.apiUrl}/api/orgs/org-2/switch`);
    request.flush({ detail: 'Organization not found' }, { status: 404, statusText: 'Not Found' });

    expect(authService.applyTokenResponse).not.toHaveBeenCalled();
    expect(localStorage.getItem('auth_token')).toBe('old-token');
    expect(localStorage.getItem('active_org_id')).toBe('org-1');
    expect(localStorage.getItem('active_org_role')).toBe('teacher');
    expect(activeOrgValues.at(-1)).toBe('org-1');
  });

  it('does not optimistically update local state before the switch response arrives', () => {
    localStorage.setItem('auth_token', 'old-token');
    localStorage.setItem('active_org_id', 'org-1');
    localStorage.setItem('active_org_role', 'teacher');
    (service as any).activeOrgSubject.next('org-1');

    service.setActiveOrg('org-2').subscribe();

    httpMock.expectOne(`${environment.apiUrl}/api/orgs/org-2/switch`);

    expect(authService.applyTokenResponse).not.toHaveBeenCalled();
    expect(localStorage.getItem('auth_token')).toBe('old-token');
    expect(localStorage.getItem('active_org_id')).toBe('org-1');
    expect(localStorage.getItem('active_org_role')).toBe('teacher');
    expect(activeOrgValues.at(-1)).toBe('org-1');
  });

  it('loads the privacy-minimized member directory for one organization', () => {
    service.getMembers('org-1').subscribe(members => expect(members[0].display_name).toBe('Ada Teacher'));
    const request = httpMock.expectOne(`${environment.apiUrl}/api/orgs/org-1/members`);
    expect(request.request.method).toBe('GET');
    request.flush([{ id: 'm1', user_id: 'u1', display_name: 'Ada Teacher', username: 'ada', role: 'teacher', status: 'active', joined_at: '2026-01-01' }]);
  });

  it('loads organization-scoped class summaries', () => {
    service.getSections('org-1').subscribe(sections => expect(sections[0].learner_count).toBe(4));
    const request = httpMock.expectOne(`${environment.apiUrl}/api/orgs/org-1/sections`);
    expect(request.request.method).toBe('GET');
    request.flush([{ id: 's1', organization_id: 'org-1', course_version_id: 'v1', name: 'Class', mode: 'remote', created_by: 'u1', learner_count: 4, teacher_count: 1 }]);
  });
});
