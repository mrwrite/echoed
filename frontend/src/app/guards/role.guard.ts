import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { PermissionsService } from '../services/permissions.service';

@Injectable({
  providedIn: 'root'
})
export class RoleGuard implements CanActivate {
  constructor(
    private authService: AuthService,
    private permissionsService: PermissionsService,
    private router: Router
  ) {}

  async canActivate(route: ActivatedRouteSnapshot): Promise<boolean> {
    const allowedRoles = route.data['roles'] as string[] | undefined;
    if (!this.authService.getToken()) {
      await this.router.navigate(['/login']);
      return false;
    }

    await this.permissionsService.bootstrapSession();

    if (!allowedRoles || allowedRoles.length === 0 || this.permissionsService.hasAnyRole(...allowedRoles)) {
      return true;
    }

    await this.router.navigate(['/access-denied']);
    return false;
  }
}
