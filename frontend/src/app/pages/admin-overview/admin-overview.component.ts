import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Subscription } from 'rxjs';

import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { AdminOverviewResponse, AnalyticsService } from '../../services/analytics.service';
import { BadgesService } from '../../services/badges.service';
import { CoursesService } from '../../services/courses.service';
import { OrganizationService } from '../../services/organization.service';
import { PermissionsService } from '../../services/permissions.service';
import { UsersService } from '../../services/users.service';

type SourceName = 'overview' | 'users' | 'organizations' | 'courses' | 'badges';

@Component({
  selector: 'app-admin-overview',
  standalone: true,
  imports: [CommonModule, RouterLink, EchoLoadingStateComponent, EchoStatePanelComponent],
  templateUrl: './admin-overview.component.html',
  styleUrl: './admin-overview.component.scss',
})
export class AdminOverviewComponent implements OnInit, OnDestroy {
  role = '';
  loading = true;
  overview?: AdminOverviewResponse;
  counts = { users: 0, organizations: 0, courses: 0, badges: 0 };
  failedSources = new Set<SourceName>();
  private readonly subscriptions = new Subscription();

  constructor(
    private readonly permissions: PermissionsService,
    private readonly analytics: AnalyticsService,
    private readonly users: UsersService,
    private readonly organizations: OrganizationService,
    private readonly courses: CoursesService,
    private readonly badges: BadgesService,
  ) {}

  ngOnInit(): void {
    this.subscriptions.add(this.permissions.user$.subscribe(user => {
      if (!user || this.role) return;
      this.role = user.role;
      this.load();
    }));
  }

  ngOnDestroy(): void { this.subscriptions.unsubscribe(); }

  get isAdmin(): boolean { return this.role === 'admin'; }

  load(): void {
    this.loading = true;
    this.failedSources.clear();
    let pending = this.isAdmin ? 5 : 2;
    const done = () => { pending -= 1; this.loading = pending > 0; };
    const fail = (source: SourceName) => { this.failedSources.add(source); done(); };

    if (this.isAdmin) {
      this.subscriptions.add(this.analytics.getAdminOverview().subscribe({ next: value => { this.overview = value; done(); }, error: () => fail('overview') }));
      this.subscriptions.add(this.users.getUsers().subscribe({ next: value => { this.counts.users = value.length; done(); }, error: () => fail('users') }));
      this.subscriptions.add(this.courses.getCourses().subscribe({ next: value => { this.counts.courses = value.length; done(); }, error: () => fail('courses') }));
    }
    this.subscriptions.add(this.organizations.refreshOrganizations().subscribe({ next: value => { this.counts.organizations = value.length; done(); }, error: () => fail('organizations') }));
    this.subscriptions.add(this.badges.getBadges().subscribe({ next: value => { this.counts.badges = value.length; done(); }, error: () => fail('badges') }));
  }
}
