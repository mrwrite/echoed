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

      <div class="ee-list" *ngIf="(items$ | async) as items">
        <ng-container *ngIf="items.length; else noItems">
          <article class="ee-list-row" *ngFor="let item of items">
            <div>
              <h2>{{ item.title }}</h2>
              <p>{{ item.subtitle }}</p>
              <span class="ee-badge" [ngClass]="badgeClass(item.status)">{{ label(item.status) }}</span>
            </div>
            <a class="ee-link-button ee-link-button--primary" *ngIf="item.detailRoute" [routerLink]="item.detailRoute">Open</a>
          </article>
        </ng-container>
      </div>

      <ng-template #noItems>
        <div class="ee-state">
          <h2>No records yet</h2>
          <p>{{ emptyText }}</p>
        </div>
      </ng-template>
    </section>
  `,
  styles: [`
    h2 { font-size: 1.05rem; margin: 0; }
    article p { color: #526273; margin: .35rem 0 .55rem; }
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
          detailRoute: `/workspace/projects/${item.id}`,
        })))));
      case 'products':
        return this.v2Platform.getProducts().pipe(switchMap(items => of(items.map(item => ({
          id: item.id,
          title: item.title,
          subtitle: `${this.label(item.product_type)}${item.course_id ? ' - course-backed runtime link' : ''}`,
          status: `${item.status} - ${item.review_state}`,
          detailRoute: `/workspace/products/${item.id}`,
        })))));
      case 'knowledge-sources':
        return this.v2Platform.getKnowledgeSources().pipe(switchMap(items => of(items.map(item => ({
          id: item.id,
          title: item.title,
          subtitle: item.citation || item.uri || this.label(item.source_type),
          status: item.status,
        })))));
      case 'artifacts':
        return this.v2Platform.getArtifacts().pipe(switchMap(items => of(items.map(item => ({
          id: item.id,
          title: item.title,
          subtitle: this.label(item.artifact_type),
          status: `${item.status} - ${item.review_state}`,
          detailRoute: `/workspace/artifacts/${item.id}`,
        })))));
      case 'generation-runs':
        return this.v2Platform.getGenerationRuns().pipe(switchMap(items => of(items.map(item => ({
          id: item.id,
          title: item.model_name || 'Generation run',
          subtitle: item.output_summary || item.prompt || 'AI execution metadata placeholder',
          status: item.status,
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
}
