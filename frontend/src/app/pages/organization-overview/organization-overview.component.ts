import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { forkJoin, of } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';

import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { Organization, OrganizationInvite, OrganizationMember } from '../../models/organization';
import { Section } from '../../models/section';
import { Product } from '../../models/v2-platform.model';
import { InvitesService } from '../../services/invites.service';
import { OrganizationService } from '../../services/organization.service';
import { V2PlatformService } from '../../services/v2-platform.service';

@Component({
  selector: 'app-organization-overview',
  standalone: true,
  imports: [CommonModule, RouterLink, EchoLoadingStateComponent, EchoStatePanelComponent],
  templateUrl: './organization-overview.component.html',
  styleUrl: './organization-overview.component.scss',
})
export class OrganizationOverviewComponent implements OnInit {
  organization?: Organization;
  members: OrganizationMember[] = [];
  invites: OrganizationInvite[] = [];
  sections: Section[] = [];
  products: Product[] = [];
  loading = true;
  loadError = '';
  partialFailures: string[] = [];

  constructor(
    private readonly organizations: OrganizationService,
    private readonly invitesService: InvitesService,
    private readonly v2Platform: V2PlatformService,
  ) {}

  ngOnInit(): void {
    this.load();
  }

  get teachers(): number {
    return this.members.filter(member => ['teacher', 'instructor'].includes(member.role)).length;
  }

  get students(): number {
    return this.members.filter(member => member.role === 'student').length;
  }

  get pendingInvites(): number {
    return this.invites.filter(invite => this.inviteStatus(invite) === 'Pending').length;
  }

  get activeSections(): number {
    const now = Date.now();
    return this.sections.filter(section => !section.end_date || new Date(section.end_date).getTime() >= now).length;
  }

  get availableCourses(): number {
    return this.products.filter(product => ['course', 'learning_path', 'certification'].includes(product.product_type)).length;
  }

  get emptySections(): Section[] {
    return this.sections.filter(section => (section.learner_count ?? 0) === 0);
  }

  load(): void {
    this.loading = true;
    this.loadError = '';
    this.partialFailures = [];
    this.organizations.refreshOrganizations().pipe(
      switchMap(organizations => {
        const activeOrgId = this.organizations.getActiveOrgId();
        this.organization = organizations.find(org => org.id === activeOrgId);
        if (!this.organization) {
          throw new Error('active-organization-missing');
        }
        const orgId = this.organization.id;
        return forkJoin({
          members: this.organizations.getMembers(orgId).pipe(catchError(() => {
            this.partialFailures.push('member counts');
            return of([] as OrganizationMember[]);
          })),
          invites: this.invitesService.listInvites(orgId).pipe(catchError(() => {
            this.partialFailures.push('invitation counts');
            return of([] as OrganizationInvite[]);
          })),
          sections: this.organizations.getSections(orgId).pipe(catchError(() => {
            this.partialFailures.push('class counts');
            return of([] as Section[]);
          })),
          products: this.v2Platform.getProducts().pipe(catchError(() => {
            this.partialFailures.push('course availability');
            return of([] as Product[]);
          })),
        });
      }),
    ).subscribe({
      next: result => {
        this.members = result.members;
        this.invites = result.invites;
        this.sections = result.sections;
        this.products = result.products;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.loadError = 'We could not load the active organization. No organization data was changed.';
      },
    });
  }

  inviteStatus(invite: OrganizationInvite): 'Accepted' | 'Expired' | 'Pending' {
    if (invite.accepted_at) {
      return 'Accepted';
    }
    return new Date(invite.expires_at).getTime() < Date.now() ? 'Expired' : 'Pending';
  }
}
