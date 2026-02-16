import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { of } from 'rxjs';
import { RoleGuard } from './role.guard';
import { AuthService } from '../services/auth.service';
import { PermissionsService } from '../services/permissions.service';

class MockAuthService {
  getToken() {
    return 'fake-token';
  }
}

class MockRouter {
  navigate = jasmine.createSpy('navigate').and.resolveTo(true);
}

describe('RoleGuard', () => {
  it('allows when any allowed role is present', async () => {
    const permissionsService = jasmine.createSpyObj<PermissionsService>(
      'PermissionsService',
      ['bootstrapSession', 'hasAnyRole'],
      { ready$: of(true) }
    );
    permissionsService.bootstrapSession.and.resolveTo();
    permissionsService.hasAnyRole.and.returnValue(true);

    TestBed.configureTestingModule({
      providers: [
        RoleGuard,
        { provide: AuthService, useClass: MockAuthService },
        { provide: PermissionsService, useValue: permissionsService },
        { provide: Router, useClass: MockRouter }
      ]
    });

    const guard = TestBed.inject(RoleGuard);
    const canActivate = await guard.canActivate({ data: { roles: ['teacher'] } } as any);
    expect(canActivate).toBe(true);
  });
});
