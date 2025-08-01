import { TestBed } from '@angular/core/testing';
import { Router, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { RoleGuard } from './role.guard';

class MockAuthService {
  token: string | null = null;
  getToken() { return this.token; }
  getTokenPayload(token: string) { return { role: 'admin' }; }
}

class MockRouter {
  navigateSpy: any[] = [];
  navigate(commands: any[]) { this.navigateSpy = commands; }
}

describe('RoleGuard', () => {
  let guard: RoleGuard;
  let authService: MockAuthService;
  let router: MockRouter;
  const route = new ActivatedRouteSnapshot();
  const state = {} as RouterStateSnapshot;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        RoleGuard,
        { provide: AuthService, useClass: MockAuthService },
        { provide: Router, useClass: MockRouter }
      ]
    });
    guard = TestBed.inject(RoleGuard);
    authService = TestBed.inject(AuthService) as unknown as MockAuthService;
    router = TestBed.inject(Router) as unknown as MockRouter;
  });

  it('should allow activation when role matches', () => {
    authService.token = 'token';
    route.data = { roles: ['admin'] } as any;
    expect(guard.canActivate(route, state)).toBeTrue();
  });

  it('should navigate to login when no token', () => {
    authService.token = null;
    route.data = { roles: ['admin'] } as any;
    expect(guard.canActivate(route, state)).toBeFalse();
    expect(router.navigateSpy[0]).toBe('/login');
  });
});
