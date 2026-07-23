import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs/operators';

import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { Organization } from '../../models/organization';
import { OrganizationService } from '../../services/organization.service';

@Component({
  selector: 'app-organization-settings',
  standalone: true,
  imports: [CommonModule, FormsModule, EchoLoadingStateComponent, EchoStatePanelComponent],
  templateUrl: './organization-settings.component.html',
  styleUrl: './organization-settings.component.scss',
})
export class OrganizationSettingsComponent implements OnInit {
  organization?: Organization;
  nameDraft = '';
  loading = true;
  saving = false;
  loadError = '';
  formError = '';
  successMessage = '';

  constructor(private readonly organizations: OrganizationService) {}

  ngOnInit(): void { this.load(); }

  load(): void {
    this.loading = true;
    this.loadError = '';
    this.organizations.refreshOrganizations().subscribe({
      next: organizations => {
        const activeOrgId = this.organizations.getActiveOrgId();
        this.organization = organizations.find(org => org.id === activeOrgId);
        this.nameDraft = this.organization?.name || '';
        this.loading = false;
        if (!this.organization) this.loadError = 'The active organization is not available in your memberships.';
      },
      error: () => { this.loading = false; this.loadError = 'We could not load organization settings. No settings were changed.'; },
    });
  }

  save(): void {
    this.formError = '';
    this.successMessage = '';
    if (!this.organization || !this.nameDraft.trim()) {
      this.formError = 'Organization name is required.';
      return;
    }
    this.saving = true;
    this.organizations.updateOrganization(this.organization.id, { name: this.nameDraft.trim() }).pipe(
      finalize(() => this.saving = false),
    ).subscribe({
      next: organization => {
        this.organization = organization;
        this.nameDraft = organization.name;
        this.successMessage = 'Organization name updated.';
        this.organizations.refreshOrganizations().subscribe();
      },
      error: error => { this.formError = error?.error?.detail || 'We could not update the organization name. No settings were changed.'; },
    });
  }

  label(value: string): string { return value.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase()); }
}
