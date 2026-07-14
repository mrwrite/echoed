import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Subscription } from 'rxjs';

import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { ReviewCenter } from '../../models/v2-platform.model';
import { AnalyticsService, V2WorkspaceAnalytics } from '../../services/analytics.service';
import { V2PlatformService } from '../../services/v2-platform.service';

type StudioSource = 'summary' | 'review';

@Component({
  selector: 'app-studio-overview',
  standalone: true,
  imports: [CommonModule, RouterLink, EchoLoadingStateComponent, EchoStatePanelComponent],
  templateUrl: './studio-overview.component.html',
  styleUrl: './studio-overview.component.scss',
})
export class StudioOverviewComponent implements OnInit, OnDestroy {
  loading = true;
  summary?: V2WorkspaceAnalytics;
  review?: ReviewCenter;
  failedSources = new Set<StudioSource>();
  private readonly subscriptions = new Subscription();

  constructor(
    private readonly analytics: AnalyticsService,
    private readonly platform: V2PlatformService,
  ) {}

  ngOnInit(): void { this.load(); }
  ngOnDestroy(): void { this.subscriptions.unsubscribe(); }

  get attentionCount(): number {
    if (!this.review) return 0;
    return this.review.pending_artifacts.length + this.review.draft_products.length + this.review.lesson_governance_items.length;
  }

  load(): void {
    this.loading = true;
    this.failedSources.clear();
    let pending = 2;
    const done = () => { pending -= 1; this.loading = pending > 0; };
    const fail = (source: StudioSource) => { this.failedSources.add(source); done(); };

    this.subscriptions.add(this.analytics.getV2WorkspaceAnalytics().subscribe({
      next: value => { this.summary = value; done(); },
      error: () => fail('summary'),
    }));
    this.subscriptions.add(this.platform.getReviewCenter().subscribe({
      next: value => { this.review = value; done(); },
      error: () => fail('review'),
    }));
  }
}
