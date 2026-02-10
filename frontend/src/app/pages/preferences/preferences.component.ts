import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PreferencesService } from '../../services/preferences.service';
import { UserPreferences } from '../../models/user-preferences';
import { ToastService } from '../../services/toast.service';
import { OrganizationService } from '../../services/organization.service';
import { Organization } from '../../models/organization';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-preferences',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './preferences.component.html',
  styleUrl: './preferences.component.scss'
})
export class PreferencesComponent implements OnInit {
  preferences: UserPreferences = {
    locale: 'en',
    timezone: '',
    theme: 'system',
    large_text: false,
    dyslexia_font: false,
    preferred_mode: 'student',
    reading_level_mode: 'standard'
  };
  organizations: Organization[] = [];
  activeOrg?: Organization;
  orgNameDraft = '';
  canManageOrg = false;

  constructor(
    private preferencesService: PreferencesService,
    private toastService: ToastService,
    private organizationService: OrganizationService,
    private authService: AuthService,
  ) {}

  ngOnInit(): void {
    this.preferencesService.loadPreferences().subscribe(prefs => {
      this.preferences = { ...prefs };
    });

    this.organizationService.refreshOrganizations().subscribe();
    this.organizationService.organizations$.subscribe((orgs) => {
      this.organizations = orgs;
      const activeOrgId = this.organizationService.getActiveOrgId();
      this.activeOrg = orgs.find((org) => org.id === activeOrgId);
      this.orgNameDraft = this.activeOrg?.name ?? '';
      this.canManageOrg = this.checkOrgPermissions();
    });
  }

  save(): void {
    this.preferencesService.updatePreferences(this.preferences).subscribe(() => {
      localStorage.setItem('locale', this.preferences.locale);
      this.toastService.show('Preferences saved!', 'success');
    });
  }

  saveOrganizationName(): void {
    if (!this.activeOrg || !this.orgNameDraft || !this.canManageOrg) {
      return;
    }
    this.organizationService
      .updateOrganization(this.activeOrg.id, { name: this.orgNameDraft })
      .subscribe({
        next: (org) => {
          this.organizationService.refreshOrganizations().subscribe();
          this.activeOrg = org;
          this.toastService.show('Organization name updated!', 'success');
        },
        error: () => {
          this.toastService.show('Unable to update organization name.', 'error');
        },
      });
  }

  private checkOrgPermissions(): boolean {
    const activeOrgRole = this.organizationService.getActiveOrgRole();
    if (activeOrgRole && ['org_admin', 'content_admin'].includes(activeOrgRole)) {
      return true;
    }
    const token = this.authService.getToken();
    const payload = token ? this.authService.getTokenPayload(token) : null;
    return payload?.role === 'super_admin';
  }
}
