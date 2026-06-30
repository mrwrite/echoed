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
          *ngIf="nextProduct && !nextProduct.is_enrolled"
          color="accent"
          label="Enroll"
          (click)="enroll(nextProduct)"
        ></app-echo-button>
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
    .learner-portal { color: #102033; display: grid; gap: 1rem; padding: clamp(1rem, 3vw, 2rem); }
    header, .panel, .summary article { background: #fff; border: 1px solid #d8e1ea; border-radius: 8px; box-shadow: 0 14px 32px rgba(16,32,51,.08); padding: clamp(1rem, 3vw, 1.5rem); }
    header p, .panel__heading p { color: #0f766e; font-size: .76rem; font-weight: 900; letter-spacing: .12em; margin: 0 0 .35rem; text-transform: uppercase; }
    h1, h2, h3 { letter-spacing: 0; margin: 0; }
    h1 { font-size: clamp(2rem, 5vw, 3rem); line-height: 1; }
    header span, .panel > p, .product p, .empty { color: #526273; }
    nav, .panel__heading, .summary, .cards { display: grid; gap: .75rem; }
    nav { grid-template-columns: repeat(auto-fit, minmax(9rem, 1fr)); }
    nav a, .panel__heading a, .product button { border-radius: 6px; font-weight: 900; padding: .65rem .85rem; text-decoration: none; }
    nav a { background: #e7f7f4; color: #0f766e; text-align: center; }
    .summary { grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr)); }
    .summary article { display: grid; gap: .2rem; }
    .summary strong { color: #0f766e; font-size: 2rem; }
    .summary span, .product span { color: #526273; font-weight: 800; }
    .panel__heading { align-items: center; display: flex; justify-content: space-between; }
    .panel__heading > span, .panel__heading a { background: #102033; color: #fff; }
    .cards { grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr)); }
    .product { border: 1px solid #d8e1ea; border-radius: 8px; display: grid; gap: .65rem; padding: 1rem; }
    .product button { background: #102033; border: 1px solid #102033; color: #fff; cursor: pointer; width: fit-content; }
    a:focus-visible, button:focus-visible { outline: 3px solid rgba(15,118,110,.25); outline-offset: 3px; }
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
