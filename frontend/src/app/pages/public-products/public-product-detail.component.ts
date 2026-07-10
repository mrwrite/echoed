import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { Product } from '../../models/v2-platform.model';
import { V2PlatformService } from '../../services/v2-platform.service';

@Component({
  selector: 'app-public-product-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <section class="product-page" *ngIf="product" aria-labelledby="product-title">
      <header [style.background-image]="heroBackground()">
        <p>{{ label(product.category || product.product_type) }}</p>
        <h1 id="product-title">{{ product.title }}</h1>
        <span>{{ product.subtitle || product.description || 'Community product preview.' }}</span>
        <button type="button" disabled>Access placeholder</button>
      </header>

      <main>
        <article>
          <h2>Overview</h2>
          <p>{{ product.description || 'Product overview will be refined as community review continues.' }}</p>
        </article>
        <article>
          <h2>Curriculum summary</h2>
          <p>{{ product.course_id ? 'Course-backed product using the existing governed lesson runtime.' : 'Runtime delivery is not connected for this product type yet.' }}</p>
        </article>
        <article>
          <h2>Outcomes</h2>
          <ul>
            <li>Understand the source-backed knowledge behind this product.</li>
            <li>Move through governed learning content when runtime access allows it.</li>
            <li>Track progress through existing EchoEd learner systems where connected.</li>
          </ul>
        </article>
        <article>
          <h2>Requirements</h2>
          <p>{{ product.audience || 'Audience and prerequisites are placeholders for community readiness.' }}</p>
        </article>
        <article>
          <h2>Resources</h2>
          <p>Resources and downloads will be connected through future product packaging work.</p>
        </article>
        <aside>
          <h2>Access</h2>
          <strong>{{ product.price_placeholder || label(product.pricing_model || 'internal') }}</strong>
          <p>Access is handled through the demo and existing governed learner runtime.</p>
        </aside>
      </main>
    </section>
  `,
  styles: [`
    .product-page { color: #102033; display: grid; gap: 1rem; }
    header { background-color: #102033; background-position: center; background-size: cover; color: #fff; display: grid; gap: 1rem; min-height: 56vh; padding: clamp(2rem, 6vw, 5rem); place-content: end start; }
    header p { color: #99f6e4; font-size: .8rem; font-weight: 900; text-transform: uppercase; }
    h1, h2 { margin: 0; }
    h1 { font-size: clamp(2.5rem, 8vw, 5.5rem); line-height: .95; max-width: 12ch; }
    header span { font-size: 1.1rem; max-width: 58ch; }
    button { background: #fff; border: 0; border-radius: 999px; color: #102033; font-weight: 900; padding: .8rem 1.1rem; width: fit-content; }
    main { display: grid; gap: 1rem; grid-template-columns: minmax(0, 1fr) minmax(16rem, 24rem); padding: clamp(1rem, 4vw, 2.5rem); }
    article, aside { background: #fff; border: 1px solid #d8e1ea; border-radius: 8px; box-shadow: 0 14px 32px rgba(16,32,51,.08); padding: 1.25rem; }
    article { grid-column: 1; }
    aside { align-self: start; grid-column: 2; grid-row: 1 / span 3; }
    p, li { color: #526273; line-height: 1.6; }
    strong { display: block; font-size: 1.4rem; margin: .5rem 0; }
    @media (max-width: 760px) {
      main { grid-template-columns: 1fr; }
      article, aside { grid-column: 1; }
    }
  `]
})
export class PublicProductDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly v2Platform = inject(V2PlatformService);
  product: Product | null = null;

  ngOnInit(): void {
    const slug = this.route.snapshot.paramMap.get('slug');
    if (!slug) {
      return;
    }
    this.v2Platform.getPublicProduct(slug).subscribe(product => {
      this.product = product;
    });
  }

  heroBackground(): string {
    return this.product?.hero_image_url ? `linear-gradient(rgba(16,32,51,.35), rgba(16,32,51,.8)), url('${this.product.hero_image_url}')` : 'linear-gradient(135deg, #102033, #0f766e)';
  }

  label(value: string): string {
    return value.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
  }
}
