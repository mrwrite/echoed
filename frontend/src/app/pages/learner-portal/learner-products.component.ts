import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { Router } from '@angular/router';
import { EchoButtonComponent } from '../../components/echo-button/echo-button.component';
import { LearnerProduct } from '../../models/v2-platform.model';
import { CoursesService } from '../../services/courses.service';
import { ToastService } from '../../services/toast.service';
import { V2PlatformService } from '../../services/v2-platform.service';

@Component({
  selector: 'app-learner-products',
  standalone: true,
  imports: [CommonModule, EchoButtonComponent],
  template: `
    <section class="learner-products" aria-labelledby="learner-products-title">
      <header>
        <p>Products</p>
        <h1 id="learner-products-title">Available and enrolled products</h1>
        <span>Course-backed products use existing enrollments, progress, and governed lesson delivery.</span>
      </header>

      <article class="queue">
        <h2>Enrolled</h2>
        <div class="grid" *ngIf="enrolledProducts.length; else noEnrolled">
          <ng-container *ngFor="let product of enrolledProducts">
            <ng-container *ngTemplateOutlet="productCard; context: { $implicit: product }"></ng-container>
          </ng-container>
        </div>
        <ng-template #noEnrolled><p class="empty">No enrolled products yet.</p></ng-template>
      </article>

      <article class="queue">
        <h2>Available</h2>
        <div class="grid" *ngIf="availableProducts.length; else noAvailable">
          <ng-container *ngFor="let product of availableProducts">
            <ng-container *ngTemplateOutlet="productCard; context: { $implicit: product }"></ng-container>
          </ng-container>
        </div>
        <ng-template #noAvailable><p class="empty">No approved or published product wrappers are available right now.</p></ng-template>
      </article>

      <ng-template #productCard let-product>
        <section class="card">
          <div>
            <h3>{{ product.title }}</h3>
            <p>{{ product.description || product.learner_visibility }}</p>
          </div>
          <dl>
            <div>
              <dt>Access</dt>
              <dd>{{ product.is_enrolled ? 'Enrolled' : 'Available' }}</dd>
            </div>
            <div>
              <dt>Wrapper</dt>
              <dd>{{ label(product.product_status || product.source) }}</dd>
            </div>
            <div>
              <dt>Governance</dt>
              <dd>{{ product.learner_visibility }}</dd>
            </div>
          </dl>
          <app-echo-button
            *ngIf="product.is_enrolled"
            color="primary"
            label="Continue"
            (click)="continueProduct(product)"
          ></app-echo-button>
          <app-echo-button
            *ngIf="!product.is_enrolled && product.course_id"
            color="accent"
            label="Enroll"
            (click)="enroll(product)"
          ></app-echo-button>
          <p class="empty" *ngIf="!product.is_enrolled && !product.course_id">Access granted. Runtime delivery is not connected yet.</p>
        </section>
      </ng-template>
    </section>
  `,
  styles: [`
    .learner-products { color: #102033; display: grid; gap: 1rem; padding: clamp(1rem, 3vw, 2rem); }
    header, .queue { background: #fff; border: 1px solid #d8e1ea; border-radius: 8px; box-shadow: 0 14px 32px rgba(16,32,51,.08); padding: clamp(1rem, 3vw, 1.5rem); }
    header p { color: #0f766e; font-size: .76rem; font-weight: 900; letter-spacing: .12em; margin: 0 0 .35rem; text-transform: uppercase; }
    h1, h2, h3 { letter-spacing: 0; margin: 0; }
    h1 { font-size: clamp(2rem, 5vw, 3rem); line-height: 1; }
    header span, .card p, .empty, dd { color: #526273; }
    .queue { display: grid; gap: .9rem; }
    .grid { display: grid; gap: .85rem; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
    .card { border: 1px solid #d8e1ea; border-radius: 8px; display: grid; gap: .75rem; padding: 1rem; }
    dl { display: grid; gap: .5rem; margin: 0; }
    dt { color: #334155; font-size: .75rem; font-weight: 900; text-transform: uppercase; }
    dd { margin: .15rem 0 0; }
  `]
})
export class LearnerProductsComponent implements OnInit {
  private readonly coursesService = inject(CoursesService);
  private readonly router = inject(Router);
  private readonly toastService = inject(ToastService);
  private readonly v2Platform = inject(V2PlatformService);

  products: LearnerProduct[] = [];

  get enrolledProducts(): LearnerProduct[] {
    return this.products.filter(product => product.is_enrolled);
  }

  get availableProducts(): LearnerProduct[] {
    return this.products.filter(product => !product.is_enrolled);
  }

  ngOnInit(): void {
    this.loadProducts();
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
        this.loadProducts();
      },
      error: () => this.toastService.show('Enrollment failed. You may already be enrolled.', 'error'),
    });
  }

  label(value: string): string {
    return value.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
  }

  private loadProducts(): void {
    this.v2Platform.getLearnerProducts().subscribe(products => {
      this.products = products;
    });
  }
}
