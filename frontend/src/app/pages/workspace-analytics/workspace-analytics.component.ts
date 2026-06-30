import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { forkJoin } from 'rxjs';
import {
  AnalyticsService,
  V2KnowledgePipelineAnalytics,
  V2LearnerAnalytics,
  V2ProductAnalytics,
  V2WorkspaceAnalytics,
} from '../../services/analytics.service';

@Component({
  selector: 'app-workspace-analytics',
  standalone: true,
  imports: [CommonModule],
  template: `
    <section class="analytics" aria-labelledby="analytics-title">
      <header>
        <p>Analytics V2</p>
        <h1 id="analytics-title">Workspace product intelligence</h1>
        <span>Read-only operational metrics from V2 wrappers and existing runtime progress.</span>
      </header>

      <div class="state" *ngIf="loading">Loading analytics...</div>
      <div class="state state--error" *ngIf="error">{{ error }}</div>

      <ng-container *ngIf="workspace && products && learners && knowledge">
        <section class="summary" aria-label="Workspace analytics summary">
          <article>
            <span>Total Products</span>
            <strong>{{ workspace.totals.total_products }}</strong>
          </article>
          <article>
            <span>Learners</span>
            <strong>{{ workspace.totals.learner_count }}</strong>
          </article>
          <article>
            <span>Enrollments</span>
            <strong>{{ workspace.totals.enrollment_count }}</strong>
          </article>
          <article>
            <span>Artifacts</span>
            <strong>{{ workspace.totals.total_artifacts }}</strong>
          </article>
        </section>

        <section class="grid">
          <article class="panel">
            <h2>Product Health</h2>
            <dl>
              <div><dt>Course-backed</dt><dd>{{ products.course_backed_product_count }}</dd></div>
              <div><dt>Program-backed</dt><dd>{{ products.program_backed_product_count }}</dd></div>
              <div><dt>By status</dt><dd>{{ formatMap(products.products_by_status) }}</dd></div>
              <div><dt>By type</dt><dd>{{ formatMap(products.products_by_type) }}</dd></div>
            </dl>
          </article>

          <article class="panel">
            <h2>Knowledge Pipeline</h2>
            <dl>
              <div><dt>Projects</dt><dd>{{ knowledge.total_projects }}</dd></div>
              <div><dt>Sources</dt><dd>{{ knowledge.total_knowledge_sources }}</dd></div>
              <div><dt>Generation runs</dt><dd>{{ knowledge.total_generation_runs }}</dd></div>
              <div><dt>Artifacts by type</dt><dd>{{ formatMap(knowledge.artifacts_by_type) }}</dd></div>
              <div><dt>Run status</dt><dd>{{ formatMap(knowledge.generation_runs_by_status) }}</dd></div>
            </dl>
          </article>

          <article class="panel">
            <h2>Learner Engagement</h2>
            <dl>
              <div><dt>Learners</dt><dd>{{ learners.summary['learner_count'] || 0 }}</dd></div>
              <div><dt>Course enrollments</dt><dd>{{ learners.summary['course_enrollment_count'] || 0 }}</dd></div>
              <div><dt>Program enrollments</dt><dd>{{ learners.summary['program_enrollment_count'] || 0 }}</dd></div>
              <div><dt>Lessons completed</dt><dd>{{ learners.summary['lesson_completion_count'] || 0 }}</dd></div>
              <div><dt>Enrollment status</dt><dd>{{ formatMap(learners.enrollments_by_status) }}</dd></div>
            </dl>
          </article>

          <article class="panel">
            <h2>Access Overview</h2>
            <dl>
              <div><dt>Total grants</dt><dd>{{ workspace.totals.total_access_grants }}</dd></div>
              <div><dt>Grant status</dt><dd>{{ formatMap(workspace.access_grants_by_status) }}</dd></div>
              <div><dt>Grant type</dt><dd>{{ formatMap(workspace.access_grants_by_type) }}</dd></div>
              <div><dt>Granted learners</dt><dd>{{ learners.summary['access_granted_learner_count'] || 0 }}</dd></div>
            </dl>
          </article>

          <article class="panel">
            <h2>Review/Publishing Health</h2>
            <dl>
              <div><dt>Draft products</dt><dd>{{ workspace.review_health['draft_products'] || 0 }}</dd></div>
              <div><dt>In review</dt><dd>{{ workspace.review_health['in_review_products'] || 0 }}</dd></div>
              <div><dt>Approved</dt><dd>{{ workspace.review_health['approved_products'] || 0 }}</dd></div>
              <div><dt>Published</dt><dd>{{ workspace.review_health['published_products'] || 0 }}</dd></div>
              <div><dt>Artifacts needing review</dt><dd>{{ workspace.review_health['review_required_artifacts'] || 0 }}</dd></div>
            </dl>
          </article>

          <article class="panel">
            <h2>Recent Activity</h2>
            <ul *ngIf="recentItems().length; else noRecent">
              <li *ngFor="let item of recentItems()">
                <span>{{ label(item.item_type) }}</span>
                <strong>{{ item.title }}</strong>
                <em>{{ label(item.status) }}</em>
              </li>
            </ul>
            <ng-template #noRecent><p>No recent wrapper activity yet.</p></ng-template>
          </article>
        </section>
      </ng-container>
    </section>
  `,
  styles: [`
    .analytics { color: #102033; display: grid; gap: 1rem; padding: clamp(1rem, 3vw, 2rem); }
    header, .panel, .summary article, .state { background: #fff; border: 1px solid #d8e1ea; border-radius: 8px; box-shadow: 0 14px 32px rgba(16,32,51,.08); padding: clamp(1rem, 3vw, 1.5rem); }
    header p { color: #0f766e; font-size: .76rem; font-weight: 900; letter-spacing: .12em; margin: 0 0 .35rem; text-transform: uppercase; }
    h1, h2 { letter-spacing: 0; margin: 0; }
    h1 { font-size: clamp(2rem, 5vw, 3rem); line-height: 1; }
    h2 { font-size: 1.1rem; }
    header span, .state, dt, li span, li em, p { color: #526273; }
    .state--error { border-color: #fecaca; color: #b91c1c; }
    .summary { display: grid; gap: .85rem; grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr)); }
    .summary article { display: grid; gap: .35rem; }
    .summary span { color: #526273; font-size: .75rem; font-weight: 900; text-transform: uppercase; }
    .summary strong { font-size: 2rem; line-height: 1; }
    .grid { display: grid; gap: .85rem; grid-template-columns: repeat(auto-fit, minmax(19rem, 1fr)); }
    .panel { display: grid; gap: .85rem; align-content: start; }
    dl { display: grid; gap: .55rem; margin: 0; }
    dl div { border-top: 1px solid #edf2f7; display: grid; gap: .2rem; padding-top: .55rem; }
    dt { font-size: .72rem; font-weight: 900; text-transform: uppercase; }
    dd { margin: 0; overflow-wrap: anywhere; }
    ul { display: grid; gap: .65rem; list-style: none; margin: 0; padding: 0; }
    li { border-top: 1px solid #edf2f7; display: grid; gap: .15rem; padding-top: .65rem; }
    li span, li em { font-size: .72rem; font-style: normal; font-weight: 900; text-transform: uppercase; }
  `]
})
export class WorkspaceAnalyticsComponent implements OnInit {
  private readonly analyticsService = inject(AnalyticsService);

  workspace: V2WorkspaceAnalytics | null = null;
  products: V2ProductAnalytics | null = null;
  learners: V2LearnerAnalytics | null = null;
  knowledge: V2KnowledgePipelineAnalytics | null = null;
  loading = true;
  error = '';

  ngOnInit(): void {
    forkJoin({
      workspace: this.analyticsService.getV2WorkspaceAnalytics(),
      products: this.analyticsService.getV2ProductAnalytics(),
      learners: this.analyticsService.getV2LearnerAnalytics(),
      knowledge: this.analyticsService.getV2KnowledgePipelineAnalytics(),
    }).subscribe({
      next: result => {
        this.workspace = result.workspace;
        this.products = result.products;
        this.learners = result.learners;
        this.knowledge = result.knowledge;
        this.loading = false;
      },
      error: () => {
        this.error = 'Unable to load Analytics V2 right now.';
        this.loading = false;
      },
    });
  }

  formatMap(values: Record<string, number> | null | undefined): string {
    const entries = Object.entries(values || {});
    if (!entries.length) {
      return 'None';
    }
    return entries.map(([key, value]) => `${this.label(key)}: ${value}`).join(', ');
  }

  label(value: string): string {
    return value.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
  }

  recentItems() {
    if (!this.workspace) {
      return [];
    }
    return [
      ...this.workspace.recent.products,
      ...this.workspace.recent.artifacts,
      ...this.workspace.recent.knowledge_sources,
    ].slice(0, 8);
  }
}
