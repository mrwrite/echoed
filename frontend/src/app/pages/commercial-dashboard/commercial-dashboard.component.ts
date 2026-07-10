import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { RouterModule } from '@angular/router';
import { Product } from '../../models/v2-platform.model';
import { V2PlatformService } from '../../services/v2-platform.service';

@Component({
  selector: 'app-commercial-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <section class="community ee-page" aria-labelledby="community-title">
      <header class="ee-page-header">
        <p class="ee-eyebrow">Community Readiness</p>
        <h1 id="community-title" class="ee-page-title">Project stewardship dashboard</h1>
        <p class="ee-page-copy">Prepare products, visibility, contribution pathways, and workspace community settings for the open-source launch.</p>
      </header>

      <section class="ee-metrics">
        <article class="ee-metric"><span>Products</span><strong>{{ products.length }}</strong></article>
        <article class="ee-metric"><span>Drafts</span><strong>{{ countStatus('draft') }}</strong></article>
        <article class="ee-metric"><span>Published</span><strong>{{ countStatus('published') }}</strong></article>
        <article class="ee-metric"><span>Community review</span><strong>{{ countStatus('in_review') }}</strong></article>
      </section>

      <section class="ee-grid ee-grid--wide">
        <article class="ee-panel">
          <h2>Visibility</h2>
          <dl><div *ngFor="let item of mapEntries(visibilityCounts())"><dt>{{ label(item[0]) }}</dt><dd>{{ item[1] }}</dd></div></dl>
        </article>
        <article class="ee-panel">
          <h2>Access Models</h2>
          <dl><div *ngFor="let item of mapEntries(pricingCounts())"><dt>{{ label(item[0]) }}</dt><dd>{{ item[1] }}</dd></div></dl>
        </article>
        <article class="ee-panel">
          <h2>Product Types</h2>
          <dl><div *ngFor="let item of mapEntries(typeCounts())"><dt>{{ label(item[0]) }}</dt><dd>{{ item[1] }}</dd></div></dl>
        </article>
        <article class="ee-panel">
          <h2>Community Signals</h2>
          <dl>
            <div><dt>Contributor onboarding</dt><dd>Tracked through GitHub issues and docs</dd></div>
            <div><dt>Educator review</dt><dd>Collected through feedback and walkthroughs</dd></div>
            <div><dt>Demo access</dt><dd>Manual grants keep the demo bounded</dd></div>
          </dl>
        </article>
      </section>

      <section class="ee-panel">
        <div class="ee-panel-header">
          <div>
            <p class="ee-eyebrow">Workspace Settings</p>
            <h2>Community placeholders</h2>
          </div>
          <span class="ee-badge ee-badge--draft">Community launch</span>
        </div>
        <div class="settings">
          <article class="ee-card--interactive" *ngFor="let section of settings"><strong>{{ section }}</strong><span>Placeholder configuration area for future community stewardship.</span></article>
        </div>
      </section>

      <section class="ee-panel">
        <div class="ee-panel-header">
          <div>
            <p class="ee-eyebrow">Inventory</p>
            <h2>Community product readiness</h2>
          </div>
          <a class="ee-link-button" routerLink="/workspace/products">Products</a>
        </div>
        <div class="ee-list">
          <article class="ee-list-card ee-card--interactive" *ngFor="let product of products">
            <div>
              <span class="ee-badge" [ngClass]="product.status === 'published' ? 'ee-badge--approved' : 'ee-badge--draft'">{{ label(product.status) }}</span>
              <h3>{{ product.title }}</h3>
              <p>{{ label(product.visibility || 'draft') }} - {{ label(product.pricing_model || 'internal') }} - {{ label(product.product_type) }}</p>
            </div>
            <a class="ee-link-button ee-link-button--primary" [routerLink]="['/workspace/products', product.id]">Manage</a>
          </article>
        </div>
      </section>
    </section>
  `,
  styles: [`
    h2, h3 { margin: 0; }
    dl { display: grid; gap: .55rem; margin: 0; }
    dl div { border-top: 1px solid var(--ee-border); display: grid; gap: .2rem; padding-top: .55rem; }
    dt { color: var(--ee-text-muted); font-size: .72rem; font-weight: 900; text-transform: uppercase; }
    dd { color: var(--ee-text-soft); margin: 0; }
    .settings { display: grid; gap: .75rem; grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr)); }
    .settings article { background: rgba(255,255,255,.045); border: 1px solid var(--ee-border); border-radius: 18px; display: grid; gap: .3rem; padding: .9rem; }
    .settings strong, h3 { color: var(--ee-text); }
    .settings span, p { color: var(--ee-text-soft); }
  `]
})
export class CommercialDashboardComponent implements OnInit {
  private readonly v2Platform = inject(V2PlatformService);
  products: Product[] = [];
  readonly settings = ['Branding', 'Documentation', 'Domains', 'Roadmap', 'AI Usage'];

  ngOnInit(): void {
    this.v2Platform.getProducts().subscribe(products => {
      this.products = products;
    });
  }

  countStatus(status: string): number {
    return this.products.filter(product => product.status === status).length;
  }

  visibilityCounts(): Record<string, number> {
    return this.countBy(product => product.visibility || 'draft');
  }

  pricingCounts(): Record<string, number> {
    return this.countBy(product => product.pricing_model || 'internal');
  }

  typeCounts(): Record<string, number> {
    return this.countBy(product => product.product_type);
  }

  mapEntries(values: Record<string, number>): [string, number][] {
    return Object.entries(values);
  }

  label(value: string): string {
    return value.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
  }

  private countBy(selector: (product: Product) => string): Record<string, number> {
    return this.products.reduce((counts, product) => {
      const key = selector(product);
      counts[key] = (counts[key] || 0) + 1;
      return counts;
    }, {} as Record<string, number>);
  }
}
