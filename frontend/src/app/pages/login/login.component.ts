import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { firstValueFrom } from 'rxjs';
import { AuthService } from '../../services/auth.service';
import { OrganizationService } from '../../services/organization.service';
import { Organization } from '../../models/organization';
import { PermissionsService } from '../../services/permissions.service';

@Component({
  selector: 'echo-login',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    FormsModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {
  username: string = '';
  password: string = '';
  errorMessage: string = '';
  showPassword = false;

  constructor(
    private router: Router,
    private authService: AuthService,
    private organizationService: OrganizationService,
    private permissionsService: PermissionsService,
  ) { }

  async login(event: Event) {
    event.preventDefault();

    try {
      await firstValueFrom(this.authService.login(this.username, this.password));
      // Bootstrap user + permissions before navigation so sidenav renders
      // immediately on first dashboard paint.
      await this.permissionsService.bootstrapSession();

      // Super admins should always land in dashboard; onboarding is only for non-super-admin users lacking org context.
      try {
        const orgs = await firstValueFrom(this.organizationService.refreshOrganizations());
        if (this.needsOnboarding(orgs)) {
          await this.router.navigateByUrl('/onboarding/organization');
          return;
        }
      } catch {
        // Onboarding lookup failed; proceed to home.
      }

      await this.router.navigateByUrl('/home');
    } catch (error: any) {
      this.errorMessage = error?.error?.detail || error?.message || 'Unable to login. Please check your credentials.';
    }
  }


  private isSuperAdminSession(): boolean {
    const token = this.authService.getToken();
    const payload = token ? this.authService.getTokenPayload(token) : null;
    return this.authService.isSuperAdminRole(payload?.role);
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
}
