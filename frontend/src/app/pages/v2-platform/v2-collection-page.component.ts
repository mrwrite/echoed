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
    <section class="collection" aria-labelledby="collection-title">
      <header>
        <p>{{ eyebrow }}</p>
        <h1 id="collection-title">{{ title }}</h1>
        <span role="status">{{ status }}</span>
      </header>

      <div class="empty" *ngIf="(items$ | async) as items">
        <ng-container *ngIf="items.length; else noItems">
          <article *ngFor="let item of items">
            <div>
              <h2>{{ item.title }}</h2>
              <p>{{ item.subtitle }}</p>
              <span>{{ item.status }}</span>
            </div>
            <a *ngIf="item.detailRoute" [routerLink]="item.detailRoute">Open</a>
          </article>
        </ng-container>
      </div>

      <ng-template #noItems>
        <div class="no-items">
          <h2>No records yet</h2>
          <p>{{ emptyText }}</p>
        </div>
      </ng-template>
    </section>
  `,
  styles: [`
    .collection { display: grid; gap: 1rem; padding: clamp(1rem, 3vw, 2rem); color: #0f172a; }
    header, article, .no-items { background: #fff; border: 1px solid rgba(15,23,42,.1); border-radius: 1.4rem; box-shadow: 0 18px 40px rgba(15,23,42,.08); padding: clamp(1rem, 3vw, 1.5rem); }
    header p { color: #0e7490; font-size: .76rem; font-weight: 900; letter-spacing: .22em; margin: 0 0 .5rem; text-transform: uppercase; }
    h1, h2 { margin: 0; letter-spacing: -.03em; }
    h1 { font-size: clamp(2rem, 5vw, 3rem); }
    header span, article span { color: #0e7490; font-weight: 800; }
    .empty { display: grid; gap: .75rem; }
    article { align-items: center; display: flex; gap: 1rem; justify-content: space-between; }
    article p, .no-items p { color: #475569; margin: .35rem 0; }
    a { background: #0f172a; border-radius: 999px; color: #fff; font-weight: 900; padding: .7rem 1rem; text-decoration: none; }
    a:focus-visible { outline: 3px solid rgba(14,116,144,.25); outline-offset: 3px; }
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

  private label(value: string): string {
    return value.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
  }
}
