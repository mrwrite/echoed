import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { RouterModule } from '@angular/router';
import { Observable } from 'rxjs';
import { ReviewCenter, ReviewCenterItem } from '../../models/v2-platform.model';
import { V2PlatformService } from '../../services/v2-platform.service';

@Component({
  selector: 'app-review-center',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <section class="review-center" aria-labelledby="review-center-title">
      <header>
        <p>Review Center</p>
        <h1 id="review-center-title">Governance and readiness review</h1>
        <span>V2 wrapper review queues use real platform data. Existing lesson governance remains the learner-visible source of truth.</span>
      </header>

      <section class="guardrails" aria-label="Review governance guardrails">
        <article>
          <strong>Artifact approval</strong>
          <span>Approves a V2 knowledge output for packaging. It does not publish runtime lessons.</span>
        </article>
        <article>
          <strong>Product approval</strong>
          <span>Moves the wrapper through review. Existing lesson readiness still controls learner delivery.</span>
        </article>
        <article>
          <strong>Blocked or needs changes</strong>
          <span>Signals trust work before packaging, publishing decisions, or runtime review.</span>
        </article>
      </section>

      <div class="queues" *ngIf="reviewCenter as center">
        <article class="queue">
          <div class="queue__heading">
            <h2>Pending Artifacts</h2>
            <span>{{ center.pending_artifacts.length }}</span>
          </div>
          <ng-container *ngIf="center.pending_artifacts.length; else noArtifacts">
            <div class="item" *ngFor="let item of center.pending_artifacts">
              <ng-container *ngTemplateOutlet="reviewItem; context: { $implicit: item, statuses: artifactStatuses }"></ng-container>
            </div>
          </ng-container>
          <ng-template #noArtifacts><p class="empty">No artifacts are waiting for wrapper review.</p></ng-template>
        </article>

        <article class="queue">
          <div class="queue__heading">
            <h2>Draft Products</h2>
            <span>{{ center.draft_products.length }}</span>
          </div>
          <ng-container *ngIf="center.draft_products.length; else noProducts">
            <div class="item" *ngFor="let item of center.draft_products">
              <ng-container *ngTemplateOutlet="reviewItem; context: { $implicit: item, statuses: productStatuses }"></ng-container>
            </div>
          </ng-container>
          <ng-template #noProducts><p class="empty">No product wrappers are waiting for review.</p></ng-template>
        </article>

        <article class="queue queue--wide">
          <div class="queue__heading">
            <h2>Lesson Governance</h2>
            <span>{{ center.lesson_governance_items.length }}</span>
          </div>
          <ng-container *ngIf="center.lesson_governance_items.length; else noLessons">
            <div class="item" *ngFor="let item of center.lesson_governance_items">
              <ng-container *ngTemplateOutlet="reviewItem; context: { $implicit: item, statuses: [] }"></ng-container>
            </div>
          </ng-container>
          <ng-template #noLessons><p class="empty">Existing governed lessons do not have visible readiness blockers.</p></ng-template>
        </article>

        <article class="queue queue--wide">
          <div class="queue__heading">
            <h2>Recent Review Activity</h2>
            <span>{{ center.recent_activity.length }}</span>
          </div>
          <p class="empty" *ngFor="let activity of center.recent_activity">{{ activity.message }}</p>
        </article>
      </div>

      <ng-template #reviewItem let-item let-statuses="statuses">
        <div class="item__main">
          <div>
            <h3>{{ item.title }}</h3>
            <p>{{ item.source_coverage }}</p>
          </div>
          <span class="badge" [class.badge--blocked]="item.blocked">{{ label(item.status) }}</span>
        </div>
        <dl>
          <div>
            <dt>Readiness</dt>
            <dd>{{ item.readiness }}</dd>
          </div>
          <div>
            <dt>Decision</dt>
            <dd>{{ item.required_decision }}</dd>
          </div>
          <div>
            <dt>Review state</dt>
            <dd>{{ label(item.review_state || item.status) }}</dd>
          </div>
        </dl>
        <div class="actions">
          <a *ngIf="item.detail_route" [routerLink]="item.detail_route">Open</a>
          <a *ngIf="item.governance_route" [routerLink]="item.governance_route">Governance</a>
          <button
            *ngFor="let status of statuses"
            type="button"
            [disabled]="item.status === status"
            (click)="updateStatus(item, status)"
          >
            {{ label(status) }}
          </button>
        </div>
      </ng-template>
    </section>
  `,
  styles: [`
    .review-center { color: var(--ee-text); display: grid; gap: 1rem; padding: clamp(1rem, 3vw, 2rem); }
    header, .queue { background: linear-gradient(145deg, rgba(255,255,255,.1), rgba(255,255,255,.035)), var(--ee-surface); border: 1px solid var(--ee-border); border-radius: var(--ee-radius); box-shadow: var(--ee-shadow-soft); backdrop-filter: blur(22px) saturate(1.2); padding: clamp(1rem, 3vw, 1.5rem); }
    header { padding: clamp(1.75rem, 5vw, 4rem); }
    header p { color: var(--ee-gold); font-size: .76rem; font-weight: 900; letter-spacing: .12em; margin: 0 0 .5rem; text-transform: uppercase; }
    h1, h2, h3 { color: var(--ee-text); letter-spacing: 0; margin: 0; }
    h1 { font-size: clamp(2.65rem, 7vw, 5.4rem); line-height: .92; max-width: 12ch; }
    header span, .empty, .item p, dd { color: var(--ee-text-soft); }
    .guardrails { display: grid; gap: .75rem; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
    .guardrails article { animation: ee-motion-card-enter var(--ee-duration-slow, 260ms) var(--ee-easing-standard, ease) both; background: rgba(255,255,255,.055); border: 1px solid var(--ee-border); border-radius: 18px; display: grid; gap: .25rem; padding: 1rem; transition: transform var(--ee-duration-base, 180ms) var(--ee-easing-standard, ease); }
    .guardrails article:hover { transform: var(--ee-hover-lift, translateY(-3px)); }
    .guardrails article:nth-child(2) { animation-delay: 45ms; }
    .guardrails article:nth-child(3) { animation-delay: 90ms; }
    .guardrails strong { color: var(--ee-text); }
    .guardrails span { color: var(--ee-text-soft); }
    .queues { display: grid; gap: 1rem; grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .queue { display: grid; gap: .9rem; align-content: start; }
    .queue--wide { grid-column: 1 / -1; }
    .queue__heading { align-items: center; display: flex; justify-content: space-between; gap: 1rem; }
    .queue__heading > span { background: rgba(92,200,255,.13); border: 1px solid rgba(92,200,255,.34); border-radius: 999px; color: #c7efff; font-weight: 900; min-width: 2rem; padding: .25rem .55rem; text-align: center; }
    .item { background: rgba(255,255,255,.045); border: 1px solid var(--ee-border); border-radius: 18px; display: grid; gap: .8rem; padding: 1rem; }
    .item__main { align-items: start; display: flex; gap: 1rem; justify-content: space-between; }
    .badge { background: rgba(167,139,250,.14); border: 1px solid rgba(167,139,250,.28); border-radius: 999px; color: #ddd4ff; font-weight: 900; padding: .28rem .65rem; transition: background var(--ee-duration-base, 180ms) var(--ee-easing-standard, ease), border-color var(--ee-duration-base, 180ms) var(--ee-easing-standard, ease); white-space: nowrap; }
    .badge--blocked { background: rgba(255,122,154,.14); border-color: rgba(255,122,154,.34); color: #ffc4d2; }
    dl { display: grid; gap: .6rem; grid-template-columns: repeat(auto-fit, minmax(11rem, 1fr)); margin: 0; }
    dt { color: var(--ee-text-muted); font-size: .78rem; font-weight: 900; text-transform: uppercase; }
    dd { margin: .15rem 0 0; }
    .actions { display: flex; flex-wrap: wrap; gap: .5rem; }
    a, button { border: 1px solid #102033; border-radius: 6px; font: inherit; font-weight: 900; padding: .55rem .75rem; text-decoration: none; }
    a { background: linear-gradient(135deg, var(--ee-purple-strong), var(--ee-purple), var(--ee-azure)); border-color: rgba(255,255,255,.18); color: #fff; transition: transform var(--ee-duration-fast, 120ms) var(--ee-easing-standard, ease); }
    button { background: rgba(255,255,255,.055); border-color: var(--ee-border); color: var(--ee-text); cursor: pointer; transition: transform var(--ee-duration-fast, 120ms) var(--ee-easing-standard, ease), opacity var(--ee-duration-base, 180ms) var(--ee-easing-standard, ease); }
    a:active, button:active { transform: var(--ee-press-scale, scale(.98)); }
    button:disabled { border-color: var(--ee-border); color: var(--ee-text-muted); cursor: default; }
    a:focus-visible, button:focus-visible { outline: 3px solid rgba(92,200,255,.25); outline-offset: 3px; }
    @media (max-width: 900px) { .queues { grid-template-columns: 1fr; } .item__main { flex-direction: column; } }
    @media (prefers-reduced-motion: reduce) { .guardrails article { animation: none; } .guardrails article:hover, a:active, button:active { transform: none; } }
  `]
})
export class ReviewCenterComponent implements OnInit {
  private readonly v2Platform = inject(V2PlatformService);

  readonly artifactStatuses = ['draft', 'in_review', 'approved', 'rejected', 'needs_changes'];
  readonly productStatuses = ['draft', 'in_review', 'approved', 'published', 'archived'];
  reviewCenter: ReviewCenter | null = null;

  ngOnInit(): void {
    this.load();
  }

  updateStatus(item: ReviewCenterItem, status: string): void {
    const request: Observable<unknown> = item.item_type === 'artifact'
      ? this.v2Platform.updateArtifactReviewStatus(item.id, { status })
      : this.v2Platform.updateProductReviewStatus(item.id, { status });

    request.subscribe(() => this.load());
  }

  label(value: string): string {
    return value.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
  }

  private load(): void {
    this.v2Platform.getReviewCenter().subscribe(center => {
      this.reviewCenter = center;
    });
  }
}
