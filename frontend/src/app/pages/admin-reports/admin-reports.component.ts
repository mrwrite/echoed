import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';

import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { AdminOverviewResponse, AnalyticsService } from '../../services/analytics.service';

@Component({
  selector: 'app-admin-reports',
  standalone: true,
  imports: [CommonModule, EchoLoadingStateComponent, EchoStatePanelComponent],
  templateUrl: './admin-reports.component.html',
  styleUrl: './admin-reports.component.scss',
})
export class AdminReportsComponent implements OnInit, OnDestroy {
  report?: AdminOverviewResponse;
  loading = true;
  failed = false;
  private readonly subscriptions = new Subscription();
  constructor(private readonly analytics: AnalyticsService) {}
  ngOnInit(): void { this.load(); }
  ngOnDestroy(): void { this.subscriptions.unsubscribe(); }
  load(): void { this.loading = true; this.failed = false; this.subscriptions.add(this.analytics.getAdminOverview().subscribe({ next: report => { this.report = report; this.loading = false; }, error: () => { this.failed = true; this.loading = false; } })); }
}
