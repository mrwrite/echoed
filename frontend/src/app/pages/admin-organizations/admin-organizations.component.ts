import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Subscription } from 'rxjs';

import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { Organization } from '../../models/organization';
import { OrganizationService } from '../../services/organization.service';

@Component({
  selector: 'app-admin-organizations',
  standalone: true,
  imports: [CommonModule, RouterLink, EchoLoadingStateComponent, EchoStatePanelComponent],
  templateUrl: './admin-organizations.component.html',
  styleUrl: './admin-organizations.component.scss',
})
export class AdminOrganizationsComponent implements OnInit, OnDestroy {
  organizations: Organization[] = [];
  selected?: Organization;
  detailMode = false;
  loading = true;
  failed = false;
  private readonly subscriptions = new Subscription();

  constructor(private readonly route: ActivatedRoute, private readonly organizationService: OrganizationService) {}
  ngOnInit(): void { this.detailMode = this.route.snapshot.paramMap.has('organizationId'); this.load(); }
  ngOnDestroy(): void { this.subscriptions.unsubscribe(); }

  load(): void {
    this.loading = true; this.failed = false;
    this.subscriptions.add(this.organizationService.refreshOrganizations().subscribe({
      next: organizations => {
        this.organizations = organizations;
        const id = this.route.snapshot.paramMap.get('organizationId');
        this.selected = id ? organizations.find(org => org.id === id) : undefined;
        this.loading = false;
      },
      error: () => { this.failed = true; this.loading = false; },
    }));
  }

  label(value?: string): string { return value ? value.replace(/_/g, ' ') : 'Not available'; }
}
