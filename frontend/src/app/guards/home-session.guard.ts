import { Injectable } from '@angular/core';
import { CanActivate, Router, UrlTree } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { AuthService } from '../services/auth.service';
import { PermissionsService } from '../services/permissions.service';
import { OrganizationService } from '../services/organization.service';
import { Organization } from '../models/organization';

@Injectable({
  providedIn: 'root'
})
export class HomeSessionGuard implements CanActivate {
  constructor(
    private authService: AuthService,
    private permissionsService: PermissionsService,
    private organizationService: OrganizationService,
    private router: Router,
  ) {}

  async canActivate(): Promise<boolean | UrlTree> {
    if (!this.authService.getToken()) {
      return this.router.parseUrl('/login');
    }

    await this.permissionsService.bootstrapSession();
    const ready = await firstValueFrom(this.permissionsService.ready$);
    if (!ready) {
      return this.router.parseUrl('/login');
    }

    try {
      const orgs = await firstValueFrom(this.organizationService.refreshOrganizations());
      // Guard-level onboarding redirect prevents home->onboarding loops and explicitly exempts super admins.
      if (this.needsOnboarding(orgs)) {
        return this.router.parseUrl('/onboarding/organization');
      }
    } catch {
      // If org lookup fails, allow dashboard shell and let page-level API errors handle UX.
    }

    return true;
  }

  private needsOnboarding(orgs: Organization[]): boolean {
    if (this.isSuperAdminSession()) {
      return false;
    }

    const pendingOrg = sessionStorage.getItem('pending_org_creation');
    if (pendingOrg) {
      return true;
    }

    if (!orgs || orgs.length === 0) {
      return true;
    }

    const hasNonPersonal = orgs.some((org) => org.type !== 'personal');
    return !hasNonPersonal;
  }

  private isSuperAdminSession(): boolean {
    const token = this.authService.getToken();
    const payload = token ? this.authService.getTokenPayload(token) : null;
    return this.authService.isSuperAdminRole(payload?.role);
  }
}
