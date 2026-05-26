import { Injectable } from '@angular/core';
import { CanActivate, Router, UrlTree } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { PermissionsService } from '../services/permissions.service';

@Injectable({
  providedIn: 'root'
})
export class HomeSessionGuard implements CanActivate {
  constructor(
    private authService: AuthService,
    private permissionsService: PermissionsService,
    private router: Router,
  ) {}

  async canActivate(): Promise<boolean | UrlTree> {
    if (!this.authService.getToken()) {
      return this.router.parseUrl('/login');
    }

    await this.permissionsService.bootstrapSession();
    const outcome = this.permissionsService.getCurrentOutcome();

    switch (outcome.status) {
      case 'ready':
        return true;
      case 'onboardingRequired':
        return this.router.parseUrl('/onboarding/organization');
      case 'unauthenticated':
      case 'failed':
      default:
        return this.router.parseUrl('/login');
    }
  }
}
