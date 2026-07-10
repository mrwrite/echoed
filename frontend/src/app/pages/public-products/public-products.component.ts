import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { RouterModule } from '@angular/router';
import { Product } from '../../models/v2-platform.model';
import { V2PlatformService } from '../../services/v2-platform.service';

@Component({
  selector: 'app-public-products',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <section class="public-products" aria-labelledby="products-title">
      <header>
        <p>Products</p>
        <h1 id="products-title">Learning products built from trusted knowledge</h1>
        <span>Public previews are ready for community review. Access actions stay bounded to the demo and existing learner runtime.</span>
      </header>

      <div class="grid" *ngIf="products.length; else empty">
        <article *ngFor="let product of products">
          <img *ngIf="product.thumbnail_url || product.hero_image_url" [src]="product.thumbnail_url || product.hero_image_url || ''" [alt]="product.title" />
          <div>
            <span>{{ label(product.category || product.product_type) }}</span>
            <h2>{{ product.title }}</h2>
            <p>{{ product.subtitle || product.description || 'Trusted learning product.' }}</p>
            <div class="badges">
              <small>{{ label(product.pricing_model || 'internal') }}</small>
              <small>{{ product.estimated_duration || 'Duration TBD' }}</small>
            </div>
            <a [routerLink]="['/products', product.slug]">View product</a>
          </div>
        </article>
      </div>

      <ng-template #empty>
        <div class="empty">
          <h2>No public products yet</h2>
          <p>Publish a Product wrapper with public visibility to preview community-facing product pages.</p>
        </div>
      </ng-template>
    </section>
  `,
  styles: [`
    .public-products { color: #102033; display: grid; gap: 1rem; padding: clamp(1rem, 4vw, 2.5rem); }
    header, article, .empty { background: #fff; border: 1px solid #d8e1ea; border-radius: 8px; box-shadow: 0 14px 32px rgba(16,32,51,.08); padding: clamp(1rem, 3vw, 1.5rem); }
    header p, article span { color: #0f766e; font-size: .76rem; font-weight: 900; text-transform: uppercase; }
    h1, h2 { margin: 0; }
    h1 { font-size: clamp(2rem, 6vw, 4rem); line-height: 1; }
    header span, article p, .empty p { color: #526273; }
    .grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(min(20rem, 100%), 1fr)); }
    article { display: grid; gap: .85rem; }
    img { aspect-ratio: 16 / 9; border-radius: 8px; object-fit: cover; width: 100%; }
    .badges { display: flex; flex-wrap: wrap; gap: .5rem; }
    small { background: #e7f7f4; border-radius: 999px; color: #0f766e; font-weight: 900; padding: .35rem .6rem; }
    a { background: #102033; border-radius: 999px; color: #fff; display: inline-block; font-weight: 900; padding: .7rem 1rem; text-decoration: none; width: fit-content; }
  `]
})
export class PublicProductsComponent implements OnInit {
  private readonly v2Platform = inject(V2PlatformService);
  products: Product[] = [];

  ngOnInit(): void {
    this.v2Platform.getPublicProducts().subscribe(products => {
      this.products = products;
    });
  }

  label(value: string): string {
    return value.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
  }
}
