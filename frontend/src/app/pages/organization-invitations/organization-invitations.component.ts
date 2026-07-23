import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs/operators';

import { EchoConfirmationDialogComponent } from '../../components/echo-confirmation-dialog/echo-confirmation-dialog.component';
import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { OrganizationInvite } from '../../models/organization';
import { InvitesService } from '../../services/invites.service';
import { OrganizationService } from '../../services/organization.service';

@Component({
  selector: 'app-organization-invitations',
  standalone: true,
  imports: [CommonModule, FormsModule, EchoConfirmationDialogComponent, EchoLoadingStateComponent, EchoStatePanelComponent],
  templateUrl: './organization-invitations.component.html',
  styleUrl: './organization-invitations.component.scss',
})
export class OrganizationInvitationsComponent implements OnInit {
  readonly roles = ['teacher', 'instructor', 'student', 'content_admin', 'org_admin'];
  invites: OrganizationInvite[] = [];
  email = '';
  role = 'teacher';
  loading = true;
  saving = false;
  loadError = '';
  formError = '';
  successMessage = '';
  confirmationOpen = false;

  constructor(private readonly invitesService: InvitesService, private readonly organizations: OrganizationService) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    const orgId = this.organizations.getActiveOrgId();
    this.loading = true;
    this.loadError = '';
    if (!orgId) {
      this.loading = false;
      this.loadError = 'Choose an active organization before reviewing invitations.';
      return;
    }
    this.invitesService.listInvites(orgId).subscribe({
      next: invites => {
        this.invites = invites;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.loadError = 'We could not load organization invitations. No invitation data was changed.';
      },
    });
  }

  requestInvite(): void {
    this.formError = '';
    this.successMessage = '';
    if (!this.email.trim()) {
      this.formError = 'Enter the email address for the invitation.';
      return;
    }
    if (['org_admin', 'content_admin'].includes(this.role)) {
      this.confirmationOpen = true;
      return;
    }
    this.createInvite();
  }

  createInvite(): void {
    const orgId = this.organizations.getActiveOrgId();
    if (!orgId || !this.email.trim()) return;
    this.saving = true;
    this.formError = '';
    this.invitesService.createInvite(orgId, { email: this.email.trim(), role: this.role }).pipe(
      finalize(() => this.saving = false),
    ).subscribe({
      next: invite => {
        this.invites = [invite, ...this.invites];
        this.successMessage = `Invitation created for ${invite.email}.`;
        this.email = '';
        this.role = 'teacher';
        this.confirmationOpen = false;
      },
      error: error => {
        this.formError = error?.error?.detail || 'We could not create this invitation. No membership was added.';
      },
    });
  }

  cancelConfirmation(): void {
    if (!this.saving) this.confirmationOpen = false;
  }

  status(invite: OrganizationInvite): 'Accepted' | 'Expired' | 'Pending' {
    if (invite.accepted_at) return 'Accepted';
    return new Date(invite.expires_at).getTime() < Date.now() ? 'Expired' : 'Pending';
  }

  label(value: string): string {
    return value.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
  }
}
