import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { RouterModule } from '@angular/router';
import { forkJoin } from 'rxjs';
import { EEMetricComponent } from '../../components/ee-design-system/ee-design-system.components';
import { ReviewCenter } from '../../models/v2-platform.model';
import { AnalyticsService, V2WorkspaceAnalytics } from '../../services/analytics.service';
import { V2PlatformService } from '../../services/v2-platform.service';

@Component({
  selector: 'app-workspace-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, EEMetricComponent],
  template: `
    <section class="ee-page" aria-labelledby="workspace-dashboard-title">
      <header class="ee-page-header">
        <p class="ee-eyebrow">Workspace</p>
        <h1 id="workspace-dashboard-title" class="ee-page-title">Knowledge product command center</h1>
        <p class="ee-page-copy">
          EchoEd turns organizational expertise into trusted learning products: knowledge comes in through projects,
          AI understanding becomes reviewable artifacts, humans govern publishing, learners receive product access,
          and analytics show what is working.
        </p>
        <div class="ee-action-row">
          <a class="ee-link-button ee-link-button--primary" routerLink="/workspace/product-studio">Open Product Studio</a>
          <a class="ee-link-button" routerLink="/workspace/demo-readiness">Demo Guide</a>
          <a class="ee-link-button" routerLink="/workspace/review-center">Review Center</a>
          <a class="ee-link-button" routerLink="/workspace/analytics">Analytics</a>
        </div>
      </header>

      <div class="ee-state" *ngIf="loading"><strong>Loading workspace signal</strong><span>Collecting V2 wrapper and runtime summaries.</span></div>
      <div class="ee-state ee-state--error" *ngIf="error"><strong>Workspace unavailable</strong><span>{{ error }}</span></div>

      <ng-container *ngIf="analytics">
        <section class="ee-metrics" aria-label="Workspace overview">
          <app-ee-metric label="Products" [value]="analytics.totals.total_products"></app-ee-metric>
          <app-ee-metric label="Projects" [value]="analytics.totals.total_projects"></app-ee-metric>
          <app-ee-metric label="Sources" [value]="analytics.totals.total_knowledge_sources"></app-ee-metric>
          <app-ee-metric label="Learners" [value]="analytics.totals.learner_count"></app-ee-metric>
        </section>

        <section class="lifecycle-strip" aria-label="EchoEd V2 lifecycle">
          <article><span>Knowledge In</span><strong>Sources enter projects</strong><p>Expert knowledge becomes reusable workspace context.</p></article>
          <article><span>AI Understanding</span><strong>Artifacts capture output</strong><p>Generation metadata is visible without executing AI yet.</p></article>
          <article><span>Review</span><strong>Governance protects trust</strong><p>Wrapper status never overrides lesson readiness.</p></article>
          <article><span>Delivery</span><strong>Products organize access</strong><p>Learners see product access while runtime rules stay authoritative.</p></article>
          <article><span>Analytics</span><strong>Health closes the loop</strong><p>Operators see pipeline, review, access, and engagement signal.</p></article>
        </section>

        <section class="ee-grid ee-grid--wide">
          <article class="ee-panel">
            <div class="ee-panel-header">
              <div>
                <p class="ee-eyebrow">Platform Flow</p>
                <h2>Workspace pipeline</h2>
              </div>
              <span class="ee-badge">V2 model</span>
            </div>
            <ol class="flow" aria-label="EchoEd V2 platform flow">
              <li>Workspace</li>
              <li>Projects</li>
              <li>Knowledge Sources</li>
              <li>Artifacts</li>
              <li>Products</li>
              <li>Review</li>
              <li>Learners</li>
              <li>Analytics</li>
            </ol>
          </article>

          <article class="ee-panel">
            <div class="ee-panel-header">
              <div>
                <p class="ee-eyebrow">Product Health</p>
                <h2>Packaging readiness</h2>
              </div>
              <a class="ee-link-button" routerLink="/workspace/products">Products</a>
            </div>
            <dl class="compact">
              <div><dt>Course-backed</dt><dd>{{ analytics.totals.course_backed_product_count }}</dd></div>
              <div><dt>Program-backed</dt><dd>{{ analytics.totals.program_backed_product_count }}</dd></div>
              <div><dt>Status</dt><dd>{{ formatMap(analytics.products_by_status) }}</dd></div>
            </dl>
          </article>

          <article class="ee-panel">
            <div class="ee-panel-header">
              <div>
                <p class="ee-eyebrow">Knowledge Pipeline</p>
                <h2>Source to artifact signal</h2>
              </div>
              <a class="ee-link-button" routerLink="/workspace/projects">Projects</a>
            </div>
            <dl class="compact">
              <div><dt>Artifacts</dt><dd>{{ analytics.totals.total_artifacts }}</dd></div>
              <div><dt>Generation runs</dt><dd>{{ analytics.totals.total_generation_runs }}</dd></div>
              <div><dt>Artifact state</dt><dd>{{ formatMap(analytics.artifacts_by_status) }}</dd></div>
            </dl>
          </article>

          <article class="ee-panel">
            <div class="ee-panel-header">
              <div>
                <p class="ee-eyebrow">Review Queue</p>
                <h2>Trust and governance</h2>
              </div>
              <a class="ee-link-button" routerLink="/workspace/review-center">Open</a>
            </div>
            <dl class="compact">
              <div><dt>Pending artifacts</dt><dd>{{ reviewCenter?.pending_artifacts?.length || 0 }}</dd></div>
              <div><dt>Draft products</dt><dd>{{ reviewCenter?.draft_products?.length || 0 }}</dd></div>
              <div><dt>Lesson readiness</dt><dd>{{ reviewCenter?.lesson_governance_items?.length || 0 }}</dd></div>
            </dl>
            <p class="ee-muted">Wrapper approval never publishes learner-visible lessons; existing governance stays authoritative.</p>
          </article>

          <article class="ee-panel">
            <div class="ee-panel-header">
              <div>
                <p class="ee-eyebrow">Learner Activity</p>
                <h2>Runtime engagement</h2>
              </div>
              <a class="ee-link-button" routerLink="/workspace/learners">Learners</a>
            </div>
            <dl class="compact">
              <div><dt>Enrollments</dt><dd>{{ analytics.totals.enrollment_count }}</dd></div>
              <div><dt>Access grants</dt><dd>{{ analytics.totals.total_access_grants }}</dd></div>
              <div><dt>Grant status</dt><dd>{{ formatMap(analytics.access_grants_by_status) }}</dd></div>
            </dl>
          </article>

          <article class="ee-panel">
            <div class="ee-panel-header">
              <div>
                <p class="ee-eyebrow">Quick Actions</p>
                <h2>Operational shortcuts</h2>
              </div>
            </div>
            <div class="ee-action-row">
              <a class="ee-link-button ee-link-button--primary" routerLink="/workspace/product-studio/create">Create product shell</a>
              <a class="ee-link-button" routerLink="/workspace/demo-readiness">Demo walkthrough</a>
              <a class="ee-link-button" routerLink="/workspace/access">Grant access</a>
              <a class="ee-link-button" routerLink="/workspace/knowledge-sources">View sources</a>
              <a class="ee-link-button" routerLink="/workspace/artifacts">Review artifacts</a>
            </div>
          </article>
        </section>

        <section class="ee-panel">
          <div class="ee-panel-header">
            <div>
              <p class="ee-eyebrow">Recent Activity</p>
              <h2>Latest wrapper updates</h2>
            </div>
          </div>
          <ul class="ee-timeline" *ngIf="recentItems().length; else emptyRecent">
            <li *ngFor="let item of recentItems()">
              <strong>{{ item.title }}</strong>
              <span class="ee-muted">{{ label(item.item_type) }} · {{ label(item.status) }}</span>
            </li>
          </ul>
          <ng-template #emptyRecent>
            <div class="ee-state"><strong>No recent wrapper activity</strong><span>Products, artifacts, and sources will appear here as the workspace takes shape.</span></div>
          </ng-template>
        </section>
      </ng-container>
    </section>
  `,
  styles: [`
    .flow { display: grid; gap: .5rem; grid-template-columns: repeat(auto-fit, minmax(8.5rem, 1fr)); list-style: none; margin: 0; padding: 0; }
    .flow li { background: rgba(255,255,255,.055); border: 1px solid var(--ee-border); border-radius: 18px; color: var(--ee-text); font-weight: 900; padding: .95rem; text-align: center; }
    .lifecycle-strip { display: grid; gap: .75rem; grid-template-columns: repeat(auto-fit, minmax(11rem, 1fr)); }
    .lifecycle-strip article { background: linear-gradient(145deg, rgba(255,255,255,.095), rgba(255,255,255,.035)); border: 1px solid var(--ee-border); border-radius: 20px; box-shadow: var(--ee-shadow-soft); display: grid; gap: .3rem; padding: 1rem; }
    .lifecycle-strip span { color: var(--ee-gold); font-size: .72rem; font-weight: 900; text-transform: uppercase; }
    .lifecycle-strip strong { color: var(--ee-text); }
    .lifecycle-strip p { color: var(--ee-text-soft); margin: 0; }
    .compact { display: grid; gap: .65rem; margin: 0; }
    .compact div { border-top: 1px solid var(--ee-border); display: grid; gap: .2rem; padding-top: .65rem; }
    dt { color: var(--ee-text-muted); font-size: .74rem; font-weight: 900; text-transform: uppercase; }
    dd { color: var(--ee-text-soft); margin: 0; overflow-wrap: anywhere; }
  `]
})
export class WorkspaceDashboardComponent implements OnInit {
  private readonly analyticsService = inject(AnalyticsService);
  private readonly v2Platform = inject(V2PlatformService);

  analytics: V2WorkspaceAnalytics | null = null;
  reviewCenter: ReviewCenter | null = null;
  loading = true;
  error = '';

  ngOnInit(): void {
    forkJoin({
      analytics: this.analyticsService.getV2WorkspaceAnalytics(),
      reviewCenter: this.v2Platform.getReviewCenter(),
    }).subscribe({
      next: result => {
        this.analytics = result.analytics;
        this.reviewCenter = result.reviewCenter;
        this.loading = false;
      },
      error: () => {
        this.error = 'Unable to load workspace dashboard data.';
        this.loading = false;
      },
    });
  }

  formatMap(values: Record<string, number> | null | undefined): string {
    const entries = Object.entries(values || {});
    return entries.length
      ? entries.map(([key, value]) => `${this.label(key)}: ${value}`).join(', ')
      : 'None';
  }

  label(value: string): string {
    return value.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
  }

  recentItems() {
    if (!this.analytics) {
      return [];
    }
    return [
      ...this.analytics.recent.products,
      ...this.analytics.recent.artifacts,
      ...this.analytics.recent.knowledge_sources,
    ].slice(0, 8);
  }
}
