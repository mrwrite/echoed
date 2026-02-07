import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { InvitesService } from '../../services/invites.service';
import { OrganizationService } from '../../services/organization.service';
import { OrganizationInvite } from '../../models/organization';
import { ToastService } from '../../services/toast.service';

@Component({
  selector: 'app-org-invites',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './org-invites.component.html',
  styleUrl: './org-invites.component.scss'
})
export class OrgInvitesComponent implements OnInit {
  invites: OrganizationInvite[] = [];
  email = '';
  role = 'teacher';
  activeOrgId: string | null = null;

  constructor(
    private invitesService: InvitesService,
    private organizationService: OrganizationService,
    private toastService: ToastService
  ) {}

  ngOnInit(): void {
    this.activeOrgId = this.organizationService.getActiveOrgId();
    if (this.activeOrgId) {
      this.loadInvites(this.activeOrgId);
    }
  }

  loadInvites(orgId: string): void {
    this.invitesService.listInvites(orgId).subscribe(invites => {
      this.invites = invites;
    });
  }

  createInvite(): void {
    if (!this.activeOrgId || !this.email) {
      return;
    }
    this.invitesService.createInvite(this.activeOrgId, { email: this.email, role: this.role }).subscribe(invite => {
      this.invites = [invite, ...this.invites];
      this.email = '';
      this.toastService.show('Invite created!', 'success');
    });
  }
}
