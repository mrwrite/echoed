import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { EchoButtonComponent } from '../../components/echo-button/echo-button.component';
import { LearnerProduct } from '../../models/v2-platform.model';
import { CoursesService } from '../../services/courses.service';
import { ToastService } from '../../services/toast.service';
import { V2PlatformService } from '../../services/v2-platform.service';

@Component({
  selector: 'app-learner-products',
  standalone: true,
  imports: [CommonModule, RouterModule, EchoButtonComponent],
  template: `
    <section class="learner-products" aria-labelledby="learner-products-title">
      <header>
        <p>Courses</p>
        <h1 id="learner-products-title">Your courses and available learning</h1>
        <span>Start or resume course-backed learning that is ready for your student account.</span>
      </header>

      <article class="queue">
        <h2>Current courses</h2>
        <div class="grid" *ngIf="enrolledProducts.length; else noEnrolled">
          <ng-container *ngFor="let product of enrolledProducts">
            <ng-container *ngTemplateOutlet="productCard; context: { $implicit: product }"></ng-container>
          </ng-container>
        </div>
        <ng-template #noEnrolled><p class="empty">No current courses yet. When you start a course, it will appear here.</p></ng-template>
      </article>

      <article class="queue">
        <h2>Available learning</h2>
        <div class="grid" *ngIf="availableProducts.length; else noAvailable">
          <ng-container *ngFor="let product of availableProducts">
            <ng-container *ngTemplateOutlet="productCard; context: { $implicit: product }"></ng-container>
          </ng-container>
        </div>
        <ng-template #noAvailable><p class="empty">No additional courses are ready for you right now.</p></ng-template>
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
              <dd>{{ product.is_enrolled ? 'In your learning' : 'Available' }}</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>{{ product.is_enrolled ? 'Ready to continue' : 'Ready to start' }}</dd>
            </div>
            <div>
              <dt>Learning access</dt>
              <dd>{{ product.learner_visibility }}</dd>
            </div>
          </dl>
          <app-echo-button
            *ngIf="product.is_enrolled"
            color="primary"
            label="Continue"
            (click)="continueProduct(product)"
          ></app-echo-button>
          <a *ngIf="product.course_id" [routerLink]="['/learn/courses', product.course_id]" class="card__link">View course path</a>
          <app-echo-button
            *ngIf="!product.is_enrolled && product.course_id"
            color="accent"
            label="Enroll"
            (click)="enroll(product)"
          ></app-echo-button>
          <p class="empty" *ngIf="!product.is_enrolled && !product.course_id">This learning item is visible to you, but course lessons are not connected yet.</p>
        </section>
      </ng-template>
    </section>
  `,
  styles: [`
    .learner-products { color: var(--ee-text); display: grid; gap: 1rem; padding: clamp(1rem, 3vw, 2rem); }
    header, .queue { background: var(--ee-surface); border: 1px solid var(--ee-border); border-radius: var(--ee-radius-lg, 8px); box-shadow: var(--ee-shadow-soft); padding: clamp(1rem, 3vw, 1.5rem); }
    header p { color: var(--ee-text-muted); font-size: .76rem; font-weight: 900; letter-spacing: .12em; margin: 0 0 .35rem; text-transform: uppercase; }
    h1, h2, h3 { letter-spacing: 0; margin: 0; }
    h1 { font-size: clamp(2rem, 5vw, 3rem); line-height: 1; }
    header span, .card p, .empty, dd { color: var(--ee-text-soft); }
    .queue { display: grid; gap: .9rem; }
    .grid { display: grid; gap: .85rem; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
    .card { background: var(--ee-surface-muted, #f8fafc); border: 1px solid var(--ee-border); border-radius: var(--ee-radius, 6px); display: grid; gap: .75rem; padding: 1rem; }
    .card__link { color: var(--ee-action-primary); font-weight: 900; text-decoration: underline; text-underline-offset: .2em; }
    dl { display: grid; gap: .5rem; margin: 0; }
    dt { color: var(--ee-text); font-size: .75rem; font-weight: 900; text-transform: uppercase; }
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
      this.toastService.show('This learning item is not connected to course lessons yet.', 'error');
      return;
    }
    this.coursesService.startCourse({ course_id: product.course_id }).subscribe({
      next: segment => {
        if (segment.delivery_state === 'governed_available' && segment.unit_progress_id) {
          this.router.navigate(['/learn/lesson', segment.unit_progress_id]);
          return;
        }
        this.toastService.show(segment.detail || 'This course is not ready for learning right now.', 'error');
      },
      error: () => this.toastService.show('Unable to continue this course right now.', 'error'),
    });
  }

  enroll(product: LearnerProduct): void {
    if (!product.course_id) {
      this.toastService.show('Starting is only available for course-backed learning right now.', 'error');
      return;
    }
    this.coursesService.enrollInCourse(product.course_id).subscribe({
      next: () => {
        this.toastService.show('Course added to your learning.', 'success');
        this.loadProducts();
      },
      error: () => this.toastService.show('We could not add this course. You may already have it.', 'error'),
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
