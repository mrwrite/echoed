import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { forkJoin } from 'rxjs';
import { EchoButtonComponent } from '../../components/echo-button/echo-button.component';
import { LearnerProduct } from '../../models/v2-platform.model';
import { CoursesService } from '../../services/courses.service';
import { ProgramsService } from '../../services/programs.service';
import { ToastService } from '../../services/toast.service';
import { V2PlatformService } from '../../services/v2-platform.service';

@Component({
  selector: 'app-learner-portal',
  standalone: true,
  imports: [CommonModule, RouterModule, EchoButtonComponent],
  template: `
    <section class="learner-portal" aria-labelledby="learner-portal-title">
      <header>
        <p>Learner Portal</p>
        <h1 id="learner-portal-title">Your products and learning paths</h1>
        <span>Products organize your access. Lessons still open through the existing governed course runtime.</span>
      </header>

      <nav aria-label="Learner portal sections">
        <a routerLink="/learn/products">Products</a>
        <a routerLink="/learn/paths">Paths</a>
        <a routerLink="/learn/certificates">Certificates</a>
        <a routerLink="/learn/resources">Resources</a>
      </nav>

      <div class="summary">
        <article>
          <strong>{{ enrolledProducts.length }}</strong>
          <span>Enrolled products</span>
        </article>
        <article>
          <strong>{{ availableProducts.length }}</strong>
          <span>Available products</span>
        </article>
        <article>
          <strong>{{ programCount }}</strong>
          <span>Learning paths</span>
        </article>
        <article>
          <strong>{{ certificateCount }}</strong>
          <span>Certificates</span>
        </article>
      </div>

      <section class="panel" aria-labelledby="next-product-heading">
        <div class="panel__heading">
          <div>
            <p>Next Action</p>
            <h2 id="next-product-heading">{{ nextProduct?.title || 'No active product yet' }}</h2>
          </div>
          <span *ngIf="nextProduct">{{ nextProduct.is_enrolled ? 'Enrolled' : 'Available' }}</span>
        </div>
        <p>{{ nextProduct?.learner_visibility || 'Enroll in a product to start a governed learning path.' }}</p>
        <app-echo-button
          *ngIf="nextProduct?.is_enrolled"
          color="primary"
          label="Continue learning"
          (click)="continueProduct(nextProduct!)"
        ></app-echo-button>
        <app-echo-button
          *ngIf="nextProduct && !nextProduct.is_enrolled && nextProduct.course_id"
          color="accent"
          label="Enroll"
          (click)="enroll(nextProduct)"
        ></app-echo-button>
        <p class="empty" *ngIf="nextProduct && !nextProduct.is_enrolled && !nextProduct.course_id">
          Access is active for this product. Runtime delivery is not connected yet.
        </p>
      </section>

      <section class="panel" aria-labelledby="enrolled-products-heading">
        <div class="panel__heading">
          <div>
            <p>Products</p>
            <h2 id="enrolled-products-heading">Current enrollments</h2>
          </div>
          <a routerLink="/learn/products">View all</a>
        </div>
        <div class="cards" *ngIf="enrolledProducts.length; else emptyProducts">
          <article class="product" *ngFor="let product of enrolledProducts | slice:0:3">
            <h3>{{ product.title }}</h3>
            <p>{{ product.description || product.learner_visibility }}</p>
            <small *ngIf="product.access_grant_id">Access grant active · governed lessons still use runtime rules</small>
            <span>{{ label(product.source) }} · {{ label(product.enrollment_status || 'enrolled') }}</span>
            <button type="button" (click)="continueProduct(product)">Continue</button>
          </article>
        </div>
        <ng-template #emptyProducts>
          <p class="empty">Your enrolled products will appear here after course enrollment.</p>
        </ng-template>
      </section>
    </section>
  `,
  styles: [`
    .learner-portal { color: var(--ee-text); display: grid; gap: 1rem; padding: clamp(1rem, 3vw, 2rem); }
    header, .panel, .summary article { animation: ee-motion-card-enter var(--ee-duration-slow, 260ms) var(--ee-easing-standard, ease) both; background: linear-gradient(145deg, rgba(255,255,255,.1), rgba(255,255,255,.035)), var(--ee-surface); border: 1px solid var(--ee-border); border-radius: var(--ee-radius); box-shadow: var(--ee-shadow-soft); backdrop-filter: blur(22px) saturate(1.2); padding: clamp(1rem, 3vw, 1.5rem); transition: transform var(--ee-duration-base, 180ms) var(--ee-easing-standard, ease); }
    .panel:hover, .summary article:hover { transform: var(--ee-hover-lift, translateY(-3px)); }
    header { padding: clamp(1.75rem, 5vw, 4rem); }
    header p, .panel__heading p { color: var(--ee-gold); font-size: .76rem; font-weight: 900; letter-spacing: .12em; margin: 0 0 .35rem; text-transform: uppercase; }
    h1, h2, h3 { color: var(--ee-text); letter-spacing: 0; margin: 0; }
    h1 { font-size: clamp(2.65rem, 7vw, 5.4rem); line-height: .92; max-width: 12ch; }
    header span, .panel > p, .product p, .empty { color: var(--ee-text-soft); }
    nav, .panel__heading, .summary, .cards { display: grid; gap: .75rem; }
    nav { grid-template-columns: repeat(auto-fit, minmax(9rem, 1fr)); }
    nav a, .panel__heading a, .product button { border-radius: 6px; font-weight: 900; padding: .65rem .85rem; text-decoration: none; }
    nav a { background: rgba(255,255,255,.055); border: 1px solid var(--ee-border); border-radius: 999px; color: var(--ee-text); text-align: center; transition: transform var(--ee-duration-base, 180ms) var(--ee-easing-standard, ease); }
    nav a:hover { transform: var(--ee-hover-lift, translateY(-3px)); }
    .summary { grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr)); }
    .summary article { display: grid; gap: .2rem; }
    .summary strong { background: linear-gradient(135deg, var(--ee-text), var(--ee-azure)); background-clip: text; color: transparent; font-size: 2rem; }
    .summary span, .product span { color: var(--ee-text-soft); font-weight: 800; }
    .product small { color: var(--ee-azure); font-weight: 800; }
    .panel__heading { align-items: center; display: flex; justify-content: space-between; }
    .panel__heading > span, .panel__heading a { background: linear-gradient(135deg, var(--ee-purple-strong), var(--ee-purple), var(--ee-azure)); border-radius: 999px; color: #fff; }
    .cards { grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr)); }
    .product { animation: ee-motion-card-enter var(--ee-duration-slow, 260ms) var(--ee-easing-standard, ease) both; background: rgba(255,255,255,.045); border: 1px solid var(--ee-border); border-radius: 18px; display: grid; gap: .65rem; padding: 1rem; transition: transform var(--ee-duration-base, 180ms) var(--ee-easing-standard, ease); }
    .product:hover { transform: var(--ee-hover-lift, translateY(-3px)); }
    .product button { background: linear-gradient(135deg, var(--ee-purple-strong), var(--ee-purple), var(--ee-azure)); border: 1px solid rgba(255,255,255,.18); color: #fff; cursor: pointer; transition: transform var(--ee-duration-fast, 120ms) var(--ee-easing-standard, ease); width: fit-content; }
    .product button:active { transform: var(--ee-press-scale, scale(.98)); }
    a:focus-visible, button:focus-visible { outline: 3px solid rgba(92,200,255,.25); outline-offset: 3px; }
    @media (prefers-reduced-motion: reduce) { header, .panel, .summary article, .product { animation: none; } .panel:hover, .summary article:hover, nav a:hover, .product:hover, .product button:active { transform: none; } }
  `]
})
export class LearnerPortalComponent implements OnInit {
  private readonly coursesService = inject(CoursesService);
  private readonly programsService = inject(ProgramsService);
  private readonly router = inject(Router);
  private readonly toastService = inject(ToastService);
  private readonly v2Platform = inject(V2PlatformService);

  products: LearnerProduct[] = [];
  programCount = 0;
  certificateCount = 0;

  get enrolledProducts(): LearnerProduct[] {
    return this.products.filter(product => product.is_enrolled);
  }

  get availableProducts(): LearnerProduct[] {
    return this.products.filter(product => !product.is_enrolled);
  }

  get nextProduct(): LearnerProduct | undefined {
    return this.enrolledProducts[0] || this.availableProducts[0];
  }

  ngOnInit(): void {
    this.v2Platform.getLearnerProducts().subscribe(products => {
      this.products = products;
    });

    forkJoin({
      programs: this.programsService.getPrograms(),
      certifications: this.programsService.getMyCertifications(),
    }).subscribe({
      next: ({ programs, certifications }) => {
        this.programCount = programs.length;
        this.certificateCount = certifications.length;
      },
      error: () => {
        this.programCount = 0;
        this.certificateCount = 0;
      },
    });
  }

  continueProduct(product: LearnerProduct): void {
    if (!product.course_id) {
      this.toastService.show('This product type is not connected to the learner runtime yet.', 'error');
      return;
    }
    this.coursesService.startCourse({ course_id: product.course_id }).subscribe({
      next: segment => {
        if (segment.delivery_state === 'governed_available' && segment.unit_progress_id) {
          this.router.navigate(['/learn/lesson', segment.unit_progress_id]);
          return;
        }
        this.toastService.show(segment.detail || 'This product is not currently available for governed learner delivery.', 'error');
      },
      error: () => this.toastService.show('Unable to continue this product right now.', 'error'),
    });
  }

  enroll(product: LearnerProduct): void {
    if (!product.course_id) {
      this.toastService.show('Enrollment is only available for course-backed products right now.', 'error');
      return;
    }
    this.coursesService.enrollInCourse(product.course_id).subscribe({
      next: () => {
        this.toastService.show('Enrollment successful.', 'success');
        this.v2Platform.getLearnerProducts().subscribe(products => {
          this.products = products;
        });
      },
      error: () => this.toastService.show('Enrollment failed. You may already be enrolled.', 'error'),
    });
  }

  label(value: string): string {
    return value.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
  }
}
