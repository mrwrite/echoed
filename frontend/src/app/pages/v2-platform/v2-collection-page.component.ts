import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { Observable, of, switchMap } from 'rxjs';
import { V2PlatformService } from '../../services/v2-platform.service';

type CollectionType = 'projects' | 'products' | 'knowledge-sources' | 'artifacts' | 'generation-runs';

interface CollectionItem {
  id: string;
  title: string;
  subtitle: string;
  status: string;
  typeLabel: string;
  traceLabel: string;
  metrics: { label: string; value: string | number }[];
  nextAction: string;
  detailRoute?: string;
}

@Component({
  selector: 'app-v2-collection-page',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <section class="collection ee-page" aria-labelledby="collection-title">
      <header class="ee-page-header">
        <p class="ee-eyebrow">{{ eyebrow }}</p>
        <h1 id="collection-title" class="ee-page-title">{{ title }}</h1>
        <span class="ee-page-copy" role="status">{{ status }}</span>
      </header>

      <div class="collection-grid" *ngIf="(items$ | async) as items">
        <ng-container *ngIf="items.length; else noItems">
          <article class="ee-list-card ee-card--interactive" *ngFor="let item of items">
            <div class="card-main">
              <div class="ee-list-card__meta">
                <span class="ee-tag">{{ item.typeLabel }}</span>
                <span class="ee-badge" [ngClass]="badgeClass(item.status)">{{ label(item.status) }}</span>
              </div>
              <h2>{{ item.title }}</h2>
              <p>{{ item.subtitle }}</p>
              <p class="trace">{{ item.traceLabel }}</p>
              <div class="ee-kpi-strip" *ngIf="item.metrics.length">
                <div class="ee-kpi" *ngFor="let metric of item.metrics">
                  <span>{{ metric.label }}</span>
                  <strong>{{ metric.value }}</strong>
                </div>
              </div>
            </div>
            <div class="card-actions">
              <span>{{ item.nextAction }}</span>
              <a class="ee-link-button ee-link-button--primary" *ngIf="item.detailRoute" [routerLink]="item.detailRoute">Open</a>
            </div>
          </article>
        </ng-container>
      </div>

      <ng-template #noItems>
        <div class="ee-empty-state">
          <h2>No records yet</h2>
          <p>{{ emptyText }}</p>
          <a class="ee-link-button ee-link-button--primary" routerLink="/workspace/product-studio">Open Product Studio</a>
        </div>
      </ng-template>
    </section>
  `,
  styles: [`
    .collection-grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(min(26rem, 100%), 1fr)); }
    .ee-list-card { align-items: stretch; }
    h2 { color: var(--ee-text); font-size: 1.25rem; letter-spacing: 0; margin: .45rem 0 0; }
    article p { color: var(--ee-text-soft); margin: .35rem 0 .55rem; }
    .trace { color: var(--ee-text-muted); font-size: .86rem; }
    .card-main { display: grid; gap: .65rem; min-width: 0; }
    .card-actions { align-content: space-between; display: grid; gap: .75rem; justify-items: end; min-width: 9rem; }
    .card-actions span { color: var(--ee-gold); font-size: .76rem; font-weight: 900; text-align: right; text-transform: uppercase; }
    @media (max-width: 720px) {
      .ee-list-card { grid-template-columns: 1fr; }
      .card-actions { justify-items: start; }
      .card-actions span { text-align: left; }
    }
  `]
})
export class V2CollectionPageComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly v2Platform = inject(V2PlatformService);

  eyebrow = '';
  title = '';
  status = '';
  emptyText = '';
  items$: Observable<CollectionItem[]> = of([]);

  ngOnInit(): void {
    this.route.data.subscribe(data => {
      const collection = data['collection'] as CollectionType;
      this.eyebrow = data['eyebrow'] as string;
      this.title = data['title'] as string;
      this.status = data['status'] as string;
      this.emptyText = data['emptyText'] as string;
      this.items$ = this.loadCollection(collection);
    });
  }

  private loadCollection(collection: CollectionType): Observable<CollectionItem[]> {
    switch (collection) {
      case 'projects':
        return this.v2Platform.getProjects().pipe(switchMap(items => of(items.map(item => ({
          id: item.id,
          title: item.name,
          subtitle: item.description || 'Project shell',
          status: item.status,
          typeLabel: 'Knowledge pipeline',
          traceLabel: `Workspace ${item.workspace_id}`,
          metrics: [
            { label: 'Sources', value: this.metadataValue(item.metadata, 'source_count') },
            { label: 'Artifacts', value: this.metadataValue(item.metadata, 'artifact_count') },
            { label: 'Products', value: this.metadataValue(item.metadata, 'product_count') },
            { label: 'Runs', value: this.metadataValue(item.metadata, 'generation_run_count') },
          ],
          nextAction: 'Build pipeline',
          detailRoute: `/workspace/projects/${item.id}`,
        })))));
      case 'products':
        return this.v2Platform.getProducts().pipe(switchMap(items => of(items.map(item => ({
          id: item.id,
          title: item.title,
          subtitle: `${this.label(item.product_type)}${item.course_id ? ' - course-backed runtime link' : ''}`,
          status: `${item.status} - ${item.review_state}`,
          typeLabel: this.label(item.product_type),
          traceLabel: item.course_id ? 'Traceable to existing course runtime' : 'V2 product wrapper only',
          metrics: [
            { label: 'Access', value: this.label(item.access_state || 'private') },
            { label: 'Visibility', value: this.label(item.visibility || 'draft') },
            { label: 'Pricing', value: this.label(item.pricing_model || 'internal') },
          ],
          nextAction: item.course_id ? 'Validate runtime link' : 'Connect runtime',
          detailRoute: `/workspace/products/${item.id}`,
        })))));
      case 'knowledge-sources':
        return this.v2Platform.getKnowledgeSources().pipe(switchMap(items => of(items.map(item => ({
          id: item.id,
          title: item.title,
          subtitle: item.citation || item.uri || this.label(item.source_type),
          status: item.status,
          typeLabel: this.label(item.source_type),
          traceLabel: item.project_id ? `Linked to project ${item.project_id}` : 'Awaiting project linkage',
          metrics: [
            { label: 'Availability', value: this.label(item.status) },
            { label: 'Import', value: 'Coming soon' },
          ],
          nextAction: 'Prepare intake',
        })))));
      case 'artifacts':
        return this.v2Platform.getArtifacts().pipe(switchMap(items => of(items.map(item => ({
          id: item.id,
          title: item.title,
          subtitle: this.label(item.artifact_type),
          status: `${item.status} - ${item.review_state}`,
          typeLabel: this.label(item.artifact_type),
          traceLabel: item.knowledge_source_id ? `Source ${item.knowledge_source_id}` : `Project ${item.project_id}`,
          metrics: [
            { label: 'Review', value: this.label(item.review_state) },
            { label: 'Status', value: this.label(item.status) },
          ],
          nextAction: 'Review traceability',
          detailRoute: `/workspace/artifacts/${item.id}`,
        })))));
      case 'generation-runs':
        return this.v2Platform.getGenerationRuns().pipe(switchMap(items => of(items.map(item => ({
          id: item.id,
          title: item.model_name || 'Generation run',
          subtitle: item.output_summary || item.prompt || 'AI execution metadata placeholder',
          status: item.status,
          typeLabel: 'Generation metadata',
          traceLabel: `Project ${item.project_id}`,
          metrics: [
            { label: 'Status', value: this.label(item.status) },
            { label: 'Execution', value: 'Future' },
          ],
          nextAction: 'Inspect run',
          detailRoute: `/workspace/product-studio/generation-runs/${item.id}`,
        })))));
    }
  }

  label(value: string): string {
    return value.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
  }

  badgeClass(value: string): string {
    const normalized = value.toLowerCase();
    if (normalized.includes('blocked') || normalized.includes('rejected')) {
      return 'ee-badge--blocked';
    }
    if (normalized.includes('draft') || normalized.includes('review') || normalized.includes('changes')) {
      return 'ee-badge--draft';
    }
    if (normalized.includes('approved') || normalized.includes('published') || normalized.includes('active')) {
      return 'ee-badge--approved';
    }
    return '';
  }

  metadataValue(metadata: Record<string, unknown>, key: string): string | number {
    const value = metadata?.[key];
    return typeof value === 'number' || typeof value === 'string' ? value : 'Not tracked';
  }
}
