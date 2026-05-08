import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { AuthService } from './auth.service';
import { environment } from '../../environments/environment';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule]
    });
    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
    localStorage.clear();
  });

  afterEach(() => {
    httpMock.verify();
    localStorage.clear();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('stores active_org_id from the login response', () => {
    service.login('teacher', 'secret').subscribe();

    const request = httpMock.expectOne(`${environment.apiUrl}/api/auth/token`);
    request.flush({
      access_token: 'token',
      token_type: 'bearer',
      active_org_id: 'org-123',
    });

    expect(localStorage.getItem('auth_token')).toBe('token');
    expect(localStorage.getItem('active_org_id')).toBe('org-123');
  });

  it('stores active_org_role from the explicit active_org_role field', () => {
    service.login('teacher', 'secret').subscribe();

    const request = httpMock.expectOne(`${environment.apiUrl}/api/auth/token`);
    request.flush({
      access_token: 'token',
      token_type: 'bearer',
      active_org_id: 'org-123',
      active_org_role: 'content_admin',
      active_organization: {
        id: 'org-123',
        name: 'Org Name',
        type: 'school',
        role: 'teacher',
      },
      organizations: [
        { id: 'org-123', role: 'teacher' },
      ],
    });

    expect(localStorage.getItem('active_org_role')).toBe('content_admin');
  });

  it('can derive active_org_role from active_organization when active_org_role is absent', () => {
    service.login('teacher', 'secret').subscribe();

    const request = httpMock.expectOne(`${environment.apiUrl}/api/auth/token`);
    request.flush({
      access_token: 'token',
      token_type: 'bearer',
      active_org_id: 'org-123',
      active_organization: {
        id: 'org-123',
        name: 'Org Name',
        type: 'school',
        role: 'org_admin',
      },
    });

    expect(localStorage.getItem('active_org_role')).toBe('org_admin');
  });

  it('supports legacy responses by deriving the role from the matching active_org_id', () => {
    service.login('teacher', 'secret').subscribe();

    const request = httpMock.expectOne(`${environment.apiUrl}/api/auth/token`);
    request.flush({
      access_token: 'token',
      token_type: 'bearer',
      active_org_id: 'org-456',
      organizations: [
        { id: 'org-123', role: 'teacher' },
        { id: 'org-456', role: 'org_admin' },
      ],
    });

    expect(localStorage.getItem('active_org_role')).toBe('org_admin');
  });

  it('does not write a fake active_org_role when no authoritative active org exists', () => {
    localStorage.setItem('active_org_role', 'stale-role');

    service.login('teacher', 'secret').subscribe();

    const request = httpMock.expectOne(`${environment.apiUrl}/api/auth/token`);
    request.flush({
      access_token: 'token',
      token_type: 'bearer',
      organizations: [
        { id: 'org-123', role: 'teacher' },
      ],
      active_org_id: null,
      active_organization: null,
    });

    expect(localStorage.getItem('active_org_role')).toBeNull();
  });

  it('no longer blindly uses organizations[0].role when active_org_id points elsewhere', () => {
    service.login('teacher', 'secret').subscribe();

    const request = httpMock.expectOne(`${environment.apiUrl}/api/auth/token`);
    request.flush({
      access_token: 'token',
      token_type: 'bearer',
      active_org_id: 'org-999',
      organizations: [
        { id: 'org-123', role: 'teacher' },
        { id: 'org-999', role: 'content_admin' },
      ],
    });

    expect(localStorage.getItem('active_org_role')).toBe('content_admin');
  });
});
