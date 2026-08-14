import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';

import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { AuditEvent } from '../../models/audit-event';
import { AuditEventsService } from '../../services/audit-events.service';
import { securityErrorMessage } from '../../services/security-error';

@Component({
  selector: 'admin-audit-events-page',
  standalone: true,
  imports: [CommonModule, FormsModule, EchoLoadingStateComponent, EchoStatePanelComponent],
  templateUrl: './admin-audit-events.component.html',
  styleUrl: './admin-audit-events.component.scss',
})
export class AdminAuditEventsComponent implements OnInit, OnDestroy {
  events: AuditEvent[] = [];
  selected?: AuditEvent;
  action = '';
  category = '';
  outcome = '';
  nextCursor?: string | null;
  loading = true;
  loadingMore = false;
  exporting = false;
  error = '';
  exportStatus = '';
  private readonly subscriptions = new Subscription();

  constructor(private readonly auditEvents: AuditEventsService) {}

  ngOnInit(): void { this.load(); }
  ngOnDestroy(): void { this.subscriptions.unsubscribe(); }

  load(cursor?: string): void {
    const append = !!cursor;
    this.error = '';
    this.selected = append ? this.selected : undefined;
    if (append) this.loadingMore = true; else { this.loading = true; this.events = []; }
    this.subscriptions.add(this.auditEvents.list({
      action: this.action || undefined,
      category: this.category || undefined,
      outcome: this.outcome || undefined,
      cursor,
      limit: 50,
    }).subscribe({
      next: page => {
        this.events = append ? [...this.events, ...page.items] : page.items;
        this.nextCursor = page.next_cursor;
        this.loading = false;
        this.loadingMore = false;
      },
      error: error => {
        this.events = [];
        this.selected = undefined;
        this.nextCursor = undefined;
        this.loading = false;
        this.loadingMore = false;
        this.error = securityErrorMessage(error, 'Audit events could not be loaded.');
      },
    }));
  }

  clearFilters(): void { this.action = ''; this.category = ''; this.outcome = ''; this.load(); }
  label(value: string): string { return value.replace(/[._-]/g, ' '); }
  stateEntries(state: AuditEvent['before_state']): [string, string | number | boolean | null][] {
    return Object.entries(state);
  }

  export(): void {
    if (this.exporting) return;
    this.exporting = true;
    this.exportStatus = '';
    this.subscriptions.add(this.auditEvents.export({
      action: this.action || undefined,
      category: this.category || undefined,
      outcome: this.outcome || undefined,
    }).subscribe({
      next: blob => {
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = 'echoed-audit-events.csv';
        anchor.click();
        URL.revokeObjectURL(url);
        this.exporting = false;
        this.exportStatus = 'Audit export downloaded.';
      },
      error: error => {
        this.exporting = false;
        this.exportStatus = securityErrorMessage(error, 'Audit export could not be created.');
      },
    }));
  }
}
