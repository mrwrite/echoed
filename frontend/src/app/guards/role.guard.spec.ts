import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { RoleGuard } from './role.guard';
import { AuthService } from '../services/auth.service';
import { OrganizationService } from '../services/organization.service';

class MockAuthService {
  getToken() {
    return 'fake-token';
  }

  getTokenPayload() {
    return { role: 'student' };
  }
}

class MockOrgService {
  getActiveOrgRole() {
    return 'teacher';
  }
}

class MockRouter {
  navigate() {}
}

describe('RoleGuard', () => {
  it('allows when org role matches', () => {
    TestBed.configureTestingModule({
      providers: [
        RoleGuard,
        { provide: AuthService, useClass: MockAuthService },
        { provide: OrganizationService, useClass: MockOrgService },
        { provide: Router, useClass: MockRouter }
      ]
    });

    const guard = TestBed.inject(RoleGuard);
    const canActivate = guard.canActivate({ data: { roles: ['teacher'] } } as any, {} as any);
    expect(canActivate).toBe(true);
  });
});
