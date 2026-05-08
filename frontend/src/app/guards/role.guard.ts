import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, Router } from '@angular/router';
import { PermissionsService } from '../services/permissions.service';

@Injectable({
  providedIn: 'root'
})
export class RoleGuard implements CanActivate {
  constructor(
    private permissionsService: PermissionsService,
    private router: Router
  ) {}

  async canActivate(route: ActivatedRouteSnapshot): Promise<boolean> {
    const allowedRoles = route.data['roles'] as string[] | undefined;
    await this.permissionsService.bootstrapSession();
    const outcome = this.permissionsService.getCurrentOutcome();

    if (outcome.status === 'unauthenticated' || outcome.status === 'failed') {
      await this.router.navigate(['/login']);
      return false;
    }

    if (outcome.status === 'onboardingRequired') {
      await this.router.navigate(['/onboarding/organization']);
      return false;
    }

    if (!allowedRoles || allowedRoles.length === 0 || this.permissionsService.hasAnyRole(...allowedRoles)) {
      return true;
    }

    await this.router.navigate(['/access-denied']);
    return false;
  }
}
