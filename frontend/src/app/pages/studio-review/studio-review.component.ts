import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Observable, Subscription } from 'rxjs';

import { EchoConfirmationDialogComponent } from '../../components/echo-confirmation-dialog/echo-confirmation-dialog.component';
import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { ReviewCenter, ReviewCenterItem } from '../../models/v2-platform.model';
import { V2PlatformService } from '../../services/v2-platform.service';

interface PendingDecision { item: ReviewCenterItem; status: string; }

@Component({
  selector: 'app-studio-review',
  standalone: true,
  imports: [CommonModule, RouterLink, EchoConfirmationDialogComponent, EchoLoadingStateComponent, EchoStatePanelComponent],
  templateUrl: './studio-review.component.html',
  styleUrl: './studio-review.component.scss',
})
export class StudioReviewComponent implements OnInit, OnDestroy {
  readonly artifactStatuses = ['draft', 'in_review', 'approved', 'needs_changes', 'rejected'];
  readonly productStatuses = ['draft', 'in_review', 'approved', 'archived'];
  review?: ReviewCenter;
  loading = true;
  failed = false;
  saving = false;
  decision?: PendingDecision;
  actionError = '';
  statusMessage = '';
  private readonly subscriptions = new Subscription();

  constructor(private readonly platform: V2PlatformService) {}
  ngOnInit(): void { this.load(); }
  ngOnDestroy(): void { this.subscriptions.unsubscribe(); }

  load(): void {
    this.loading = true; this.failed = false;
    this.subscriptions.add(this.platform.getReviewCenter().subscribe({ next: review => { this.review = review; this.loading = false; }, error: () => { this.failed = true; this.loading = false; } }));
  }

  requestDecision(item: ReviewCenterItem, status: string): void { if (item.status !== status) { this.actionError = ''; this.decision = { item, status }; } }
  cancelDecision(): void { if (!this.saving) this.decision = undefined; }
  applyDecision(): void {
    if (!this.decision || this.saving) return;
    const { item, status } = this.decision;
    this.saving = true; this.actionError = '';
    const request: Observable<unknown> = item.item_type === 'artifact'
      ? this.platform.updateArtifactReviewStatus(item.id, { status })
      : this.platform.updateProductReviewStatus(item.id, { status });
    this.subscriptions.add(request.subscribe({
      next: () => { this.saving = false; this.decision = undefined; this.statusMessage = `“${item.title}” moved to ${this.label(status)}.`; this.load(); },
      error: () => { this.saving = false; this.actionError = 'The review state was not changed. Review the item and try again.'; },
    }));
  }

  detailRoute(item: ReviewCenterItem): string | null { return item.item_type === 'artifact' ? `/studio/drafts/${item.id}` : item.item_type === 'product' ? `/studio/content/${item.id}` : null; }
  statuses(item: ReviewCenterItem): string[] { return item.item_type === 'artifact' ? this.artifactStatuses : item.item_type === 'product' ? this.productStatuses : []; }
  label(value: string): string { return value.replace(/_/g, ' ').replace(/\b\w/g, character => character.toUpperCase()); }
  statusClass(item: ReviewCenterItem): string { return item.blocked || ['rejected', 'archived'].includes(item.status) ? 'studio-status--danger' : ['approved', 'published'].includes(item.status) ? 'studio-status--success' : 'studio-status--warning'; }
  get decisionTitle(): string { return this.decision ? `Move this ${this.decision.item.item_type === 'artifact' ? 'content draft' : 'learning offering'} to ${this.label(this.decision.status)}?` : 'Confirm review decision'; }
  get decisionDescription(): string {
    if (!this.decision) return '';
    if (this.decision.status === 'approved') return 'This records wrapper approval. It does not publish course lessons or make learner content available.';
    if (this.decision.status === 'archived') return 'This removes the wrapper from active review work. The current API does not provide a restore-specific action or audit history.';
    if (this.decision.status === 'rejected') return 'This records rejection for the content draft. It does not delete the draft or its source records.';
    if (this.decision.status === 'needs_changes') return 'This records that revision is required. Existing draft content and source associations remain in place.';
    return 'This changes the wrapper review state only. Learner-visible lesson governance remains unchanged.';
  }
}
