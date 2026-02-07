import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, Router, RouterStateSnapshot } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { OrganizationService } from '../services/organization.service';

@Injectable({
  providedIn: 'root'
})
export class RoleGuard implements CanActivate {
  constructor(
    private authService: AuthService,
    private organizationService: OrganizationService,
    private router: Router
  ) {}

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): boolean {
    const allowedRoles = route.data['roles'] as string[] | undefined;
    const token = this.authService.getToken();
    if (!token) {
      this.router.navigate(['/login']);
      return false;
    }

    const payload = this.authService.getTokenPayload(token);
    const userRole = payload?.role;
    const orgRole = this.organizationService.getActiveOrgRole();
    if (!allowedRoles || allowedRoles.length === 0 || allowedRoles.includes(userRole) || (orgRole && allowedRoles.includes(orgRole))) {
      return true;
    }

    this.router.navigate(['/access-denied']);
    return false;
  }
}
