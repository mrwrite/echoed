import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { map } from 'rxjs';

interface V2PlatformLink {
  label: string;
  route: string;
}

interface V2PlatformPageData {
  eyebrow: string;
  title: string;
  description: string;
  status: string;
  links?: V2PlatformLink[];
}

@Component({
  selector: 'app-v2-platform-page',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <section class="v2-page" *ngIf="page$ | async as page" aria-labelledby="v2-platform-title">
      <div class="v2-page__hero">
        <p class="v2-page__eyebrow">{{ page.eyebrow }}</p>
        <h1 id="v2-platform-title">{{ page.title }}</h1>
        <p class="v2-page__description">{{ page.description }}</p>
        <p class="v2-page__status" role="status">{{ page.status }}</p>
      </div>

      <div class="v2-page__actions" *ngIf="page.links?.length">
        <a
          *ngFor="let link of page.links"
          class="v2-page__link"
          [routerLink]="link.route"
        >
          {{ link.label }}
        </a>
      </div>
    </section>
  `,
  styles: [`
    .v2-page {
      display: grid;
      gap: 1rem;
      padding: clamp(1rem, 3vw, 2rem);
    }

    .v2-page__hero {
      border: 1px solid rgba(15, 23, 42, 0.1);
      border-radius: 1.5rem;
      background:
        radial-gradient(circle at top right, rgba(14, 116, 144, 0.16), transparent 34rem),
        linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
      box-shadow: 0 20px 45px rgba(15, 23, 42, 0.08);
      color: #0f172a;
      padding: clamp(1.5rem, 4vw, 3rem);
    }

    .v2-page__eyebrow {
      color: #0e7490;
      font-size: 0.78rem;
      font-weight: 800;
      letter-spacing: 0.22em;
      margin: 0 0 0.75rem;
      text-transform: uppercase;
    }

    h1 {
      font-size: clamp(1.75rem, 4vw, 3rem);
      font-weight: 900;
      letter-spacing: -0.04em;
      line-height: 1;
      margin: 0;
    }

    .v2-page__description {
      color: #334155;
      font-size: clamp(1rem, 2vw, 1.15rem);
      line-height: 1.7;
      margin: 1rem 0 0;
      max-width: 68ch;
    }

    .v2-page__status {
      border-left: 4px solid #0e7490;
      color: #164e63;
      font-weight: 700;
      margin: 1.25rem 0 0;
      padding-left: 0.85rem;
    }

    .v2-page__actions {
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
    }

    .v2-page__link {
      align-items: center;
      background: #0f172a;
      border-radius: 999px;
      color: #ffffff;
      display: inline-flex;
      font-weight: 800;
      min-height: 2.75rem;
      padding: 0.75rem 1.1rem;
      text-decoration: none;
      transition: background 160ms ease, transform 160ms ease;
    }

    .v2-page__link:hover,
    .v2-page__link:focus-visible {
      background: #0e7490;
      outline: 3px solid rgba(14, 116, 144, 0.25);
      outline-offset: 3px;
      transform: translateY(-1px);
    }
  `]
})
export class V2PlatformPageComponent {
  private readonly route = inject(ActivatedRoute);

  readonly page$ = this.route.data.pipe(
    map(data => data as V2PlatformPageData)
  );
}
