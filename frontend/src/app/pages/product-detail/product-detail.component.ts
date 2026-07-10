import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { Product } from '../../models/v2-platform.model';
import { V2PlatformService } from '../../services/v2-platform.service';

@Component({
  selector: 'app-product-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <section class="detail" *ngIf="product" aria-labelledby="product-title">
      <a routerLink="/workspace/products">Back to products</a>
      <article>
        <p>Product</p>
        <h1 id="product-title">{{ product.title }}</h1>
        <div class="badges">
          <span class="ee-badge">{{ label(product.product_type) }}</span>
          <span class="ee-badge" [ngClass]="badgeClass(product.status)">{{ label(product.status) }}</span>
          <span class="ee-badge" [ngClass]="badgeClass(product.review_state)">{{ label(product.review_state) }}</span>
        </div>
        <span>{{ label(product.product_type) }} · {{ product.status }} · {{ product.review_state }}</span>
        <p class="description">{{ product.description || 'No description yet.' }}</p>
        <div class="badges">
          <span class="ee-badge">{{ label(product.visibility || 'draft') }}</span>
          <span class="ee-badge">{{ label(product.pricing_model || 'internal') }}</span>
          <span class="ee-badge" *ngIf="product.featured">Featured</span>
          <span class="ee-badge" *ngIf="product.certificate_available">Certificate</span>
        </div>

        <div class="grid">
          <div>
            <strong>Workspace</strong>
            <span>{{ product.workspace_id }}</span>
          </div>
          <div>
            <strong>Project</strong>
            <span>{{ product.project_id || 'Not connected yet' }}</span>
          </div>
          <div>
            <strong>Runtime course</strong>
            <span>{{ product.course_id || 'No course runtime link' }}</span>
          </div>
          <div>
            <strong>Access</strong>
            <span>{{ product.access_state }}</span>
          </div>
          <div>
            <strong>Public URL</strong>
            <span>{{ product.slug ? '/products/' + product.slug : 'Generated when published' }}</span>
          </div>
          <div>
            <strong>Access model</strong>
            <span>{{ product.price_placeholder || label(product.pricing_model || 'internal') }}</span>
          </div>
        </div>

        <div class="actions">
          <button type="button" (click)="publishWrapper()" [disabled]="publishing">
            {{ publishing ? 'Publishing...' : 'Publish wrapper only' }}
          </button>
          <a *ngIf="product.slug" [routerLink]="['/products', product.slug]">Preview public page</a>
        </div>

        <div class="notice">
          Product shell details are additive. Wrapper publishing does not override existing lesson governance, create enrollments, or expose runtime lessons outside existing readiness rules.
        </div>
      </article>
    </section>
  `,
  styles: [`
    .detail { display: grid; gap: 1rem; padding: clamp(1rem, 3vw, 2rem); color: #0f172a; }
    article { background: #fff; border: 1px solid rgba(15,23,42,.1); border-radius: 1.5rem; box-shadow: 0 18px 40px rgba(15,23,42,.08); display: grid; gap: 1rem; padding: clamp(1rem, 4vw, 2rem); }
    article > p:first-child { color: #0e7490; font-size: .76rem; font-weight: 900; letter-spacing: .22em; margin: 0; text-transform: uppercase; }
    h1 { font-size: clamp(2rem, 5vw, 3rem); letter-spacing: -.04em; line-height: 1; margin: 0; }
    .description { color: #475569; font-size: 1.05rem; line-height: 1.7; }
    .grid { display: grid; gap: .75rem; grid-template-columns: repeat(auto-fit, minmax(13rem, 1fr)); }
    .grid div, .notice { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 1rem; display: grid; gap: .35rem; padding: .9rem; }
    .actions { display: flex; flex-wrap: wrap; gap: .75rem; }
    .actions button, .actions a { border-radius: 999px; font-weight: 900; min-height: 2.5rem; padding: .7rem 1rem; }
    .actions button { background: #0f172a; border: 0; color: #fff; cursor: pointer; }
    .actions button:disabled { background: #94a3b8; cursor: not-allowed; }
    .actions a { background: #e7f7f4; text-decoration: none; }
    strong { color: #334155; }
    span { color: #0e7490; font-weight: 800; overflow-wrap: anywhere; }
    .badges { display: flex; flex-wrap: wrap; gap: .5rem; }
    a { color: #0e7490; font-weight: 900; }
  `]
})
export class ProductDetailComponent implements OnInit {
  product: Product | null = null;
  publishing = false;

  constructor(
    private readonly route: ActivatedRoute,
    private readonly v2Platform: V2PlatformService,
  ) {}

  ngOnInit(): void {
    const productId = this.route.snapshot.paramMap.get('productId');
    if (!productId) {
      return;
    }
    this.v2Platform.getProduct(productId).subscribe(product => {
      this.product = product;
    });
  }

  label(value: string): string {
    return value.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
  }

  badgeClass(value: string): string {
    if (['approved', 'published', 'active'].includes(value)) {
      return 'ee-badge--approved';
    }
    if (['rejected', 'blocked', 'revoked', 'archived'].includes(value)) {
      return 'ee-badge--blocked';
    }
    if (['draft', 'in_review', 'needs_changes', 'not_reviewed'].includes(value)) {
      return 'ee-badge--draft';
    }
    return '';
  }

  publishWrapper(): void {
    if (!this.product) {
      return;
    }
    this.publishing = true;
    this.v2Platform.publishProduct(this.product.id, { visibility: 'public' }).subscribe({
      next: product => {
        this.product = product;
        this.publishing = false;
      },
      error: () => {
        this.publishing = false;
      },
    });
  }
}
