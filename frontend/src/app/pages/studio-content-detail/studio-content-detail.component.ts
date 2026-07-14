import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Subscription } from 'rxjs';

import { EchoConfirmationDialogComponent } from '../../components/echo-confirmation-dialog/echo-confirmation-dialog.component';
import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { Product } from '../../models/v2-platform.model';
import { V2PlatformService } from '../../services/v2-platform.service';

@Component({
  selector: 'app-studio-content-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, EchoConfirmationDialogComponent, EchoLoadingStateComponent, EchoStatePanelComponent],
  templateUrl: './studio-content-detail.component.html',
  styleUrl: './studio-content-detail.component.scss',
})
export class StudioContentDetailComponent implements OnInit, OnDestroy {
  product?: Product;
  loading = true;
  failed = false;
  publishing = false;
  confirmPublish = false;
  actionError = '';
  successMessage = '';
  private productId = '';
  private readonly subscriptions = new Subscription();

  constructor(private readonly route: ActivatedRoute, private readonly platform: V2PlatformService) {}

  ngOnInit(): void { this.productId = this.route.snapshot.paramMap.get('productId') || ''; this.load(); }
  ngOnDestroy(): void { this.subscriptions.unsubscribe(); }

  load(): void {
    if (!this.productId) { this.failed = true; this.loading = false; return; }
    this.loading = true;
    this.failed = false;
    this.subscriptions.add(this.platform.getProduct(this.productId).subscribe({
      next: product => { this.product = product; this.loading = false; },
      error: () => { this.failed = true; this.loading = false; },
    }));
  }

  requestPublish(): void { if (this.product && this.product.status !== 'published') { this.actionError = ''; this.confirmPublish = true; } }
  publish(): void {
    if (!this.product || this.publishing) return;
    this.publishing = true;
    this.actionError = '';
    this.subscriptions.add(this.platform.publishProduct(this.product.id, { visibility: 'public' }).subscribe({
      next: product => { this.product = product; this.publishing = false; this.confirmPublish = false; this.successMessage = 'The learning-offering wrapper is now publicly visible.'; },
      error: () => { this.publishing = false; this.actionError = 'Publishing failed. The displayed state has not changed.'; },
    }));
  }

  label(value: string): string { return value.replace(/_/g, ' ').replace(/\b\w/g, character => character.toUpperCase()); }
  statusClass(status: string): string { return ['published', 'approved'].includes(status) ? 'studio-status--success' : ['archived', 'rejected'].includes(status) ? 'studio-status--danger' : 'studio-status--warning'; }
}
