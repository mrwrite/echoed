import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { take } from 'rxjs/operators';

import { EchoButtonComponent } from '../../components/echo-button/echo-button.component';
import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { StudentBadge } from '../../models/badge';
import { Course } from '../../models/course';
import { Program, StudentCertification } from '../../models/program';
import { ContinuationGuidance, StudentCourseWithDetails } from '../../models/student-course-with-details.model';
import { LearnerProduct } from '../../models/v2-platform.model';
import { AnalyticsService, StudentProgressResponse } from '../../services/analytics.service';
import { BadgesService } from '../../services/badges.service';
import { CoursesService } from '../../services/courses.service';
import { PermissionsService } from '../../services/permissions.service';
import { ProgramsService } from '../../services/programs.service';
import { ToastService } from '../../services/toast.service';
import { V2PlatformService } from '../../services/v2-platform.service';

@Component({
  selector: 'app-learner-portal',
  standalone: true,
  imports: [CommonModule, RouterModule, EchoButtonComponent, EchoLoadingStateComponent, EchoStatePanelComponent],
  template: `
    <section class="learn-home" aria-labelledby="learn-home-title">
      <header class="learn-home__hero">
        <div>
          <p class="learn-home__eyebrow">Learn</p>
          <h1 id="learn-home-title">Continue your learning</h1>
          <p class="learn-home__intro">
            Start with your next lesson, review your progress, and find learning paths that are ready for you.
          </p>
        </div>
        <nav class="learn-home__quick-nav" aria-label="Student learning sections">
          <a routerLink="/learn/products">Courses</a>
          <a routerLink="/learn/paths">Learning paths</a>
          <a routerLink="/learn/certificates">Achievements</a>
          <a routerLink="/learn/resources">Resources</a>
        </nav>
      </header>

      <section class="learn-home__grid learn-home__grid--top">
        <article class="learn-card learn-card--priority" aria-labelledby="continue-learning-heading">
          <div class="learn-card__heading">
            <div>
              <p class="learn-home__eyebrow">Next learning</p>
              <h2 id="continue-learning-heading">{{ continuationTitle }}</h2>
            </div>
            <span *ngIf="activeStudentCourse" class="learn-status">{{ activeCourseStatusLabel }}</span>
          </div>

          <app-echo-loading-state
            *ngIf="coursesLoading"
            density="section"
            ariaLabel="learn-continuation-loading"
            title="Preparing your next lesson"
            body="We are restoring your current learning path."
          ></app-echo-loading-state>

          <app-echo-state-panel
            *ngIf="!coursesLoading && coursesLoadError"
            variant="error"
            eyebrow="Learning path unavailable"
            title="We could not restore your learning"
            [body]="coursesLoadError"
            actionLabel="Retry"
            (action)="retryCourseLoad()"
          ></app-echo-state-panel>

          <ng-container *ngIf="!coursesLoading && !coursesLoadError && activeStudentCourse">
            <p class="learn-card__title" data-testid="student-active-course-title">{{ activeStudentCourse.course.title }}</p>
            <p class="learn-card__copy">{{ activeStudentCourse.course.description }}</p>
            <p class="learn-card__guidance">{{ activeStudentCourseReason }}</p>

            <div class="learn-progress" aria-labelledby="active-progress-label">
              <div>
                <span id="active-progress-label">Your progress</span>
                <strong>{{ activeCourseProgress | number:'1.0-0' }}%</strong>
              </div>
              <div class="learn-progress__track">
                <div
                  class="learn-progress__bar"
                  [style.width.%]="activeCourseProgress"
                  role="progressbar"
                  aria-label="Active course progress"
                  [attr.aria-valuenow]="activeCourseProgress"
                  aria-valuemin="0"
                  aria-valuemax="100"
                ></div>
              </div>
            </div>

            <div *ngIf="activeContinuationState !== 'normal' || activeReinforcementMessage" class="learn-support" [attr.data-support-state]="activeContinuationState">
              <p class="learn-support__label">{{ activeContinuationEyebrow }}</p>
              <p class="learn-support__title">{{ activeContinuationTitle }}</p>
              <p *ngIf="activeReinforcementMessage">{{ activeReinforcementMessage }}</p>
              <ul *ngIf="activePrompts.length">
                <li *ngFor="let prompt of activePrompts">{{ prompt }}</li>
              </ul>
            </div>

            <app-echo-button
              color="primary"
              [label]="getCourseActionLabel(activeStudentCourse)"
              ariaLabel="Continue your next learning step"
              data-testid="student-continue-learning"
              (click)="startCourse(activeStudentCourse)"
            ></app-echo-button>
            <a class="learn-card__secondary-action" [routerLink]="['/learn/courses', activeStudentCourse.course_id]">View course path</a>
          </ng-container>

          <app-echo-state-panel
            *ngIf="!coursesLoading && !coursesLoadError && !activeStudentCourse"
            variant="empty"
            eyebrow="No active lesson"
            [title]="noContinuationTitle"
            [body]="noContinuationBody"
            actionLabel="Explore courses"
            (action)="goToCourses()"
          ></app-echo-state-panel>
        </article>

        <aside class="learn-card" aria-labelledby="progress-summary-heading">
          <p class="learn-home__eyebrow">Your progress</p>
          <h2 id="progress-summary-heading">Learning summary</h2>
          <div class="learn-summary" aria-label="Student progress summary">
            <div>
              <strong>{{ inProgressCourseCount }}</strong>
              <span>In progress</span>
            </div>
            <div>
              <strong>{{ coursesCompleted }}</strong>
              <span>Courses complete</span>
            </div>
            <div>
              <strong>{{ lessonsCompleted }}</strong>
              <span>Lessons complete</span>
            </div>
            <div>
              <strong>{{ earnedAchievementCount }}</strong>
              <span>Achievements</span>
            </div>
          </div>
        </aside>
      </section>

      <section class="learn-card" aria-labelledby="active-learning-heading">
        <div class="learn-card__heading">
          <div>
            <p class="learn-home__eyebrow">Assigned or active learning</p>
            <h2 id="active-learning-heading">Your current courses</h2>
          </div>
          <a routerLink="/learn/products">View all courses</a>
        </div>
        <app-echo-loading-state
          *ngIf="coursesLoading"
          density="section"
          ariaLabel="active-learning-loading"
          title="Loading your courses"
          body="We are preparing your current learning."
        ></app-echo-loading-state>
        <app-echo-state-panel
          *ngIf="!coursesLoading && coursesLoadError"
          variant="error"
          eyebrow="Courses unavailable"
          title="We could not load your courses"
          [body]="coursesLoadError"
          actionLabel="Retry"
          (action)="retryCourseLoad()"
        ></app-echo-state-panel>
        <div *ngIf="!coursesLoading && !coursesLoadError && studentCourses.length" class="learning-list">
          <article class="learning-item" *ngFor="let course of studentCourses | slice:0:4">
            <div>
              <span class="learn-status">{{ statusLabel(course.status, course.progress) }}</span>
              <h3>{{ course.course.title }}</h3>
              <p>{{ course.course.description }}</p>
            </div>
            <div class="learn-progress learn-progress--compact">
              <div>
                <span>Progress</span>
                <strong>{{ normalizedProgress(course.progress) | number:'1.0-0' }}%</strong>
              </div>
              <div class="learn-progress__track">
                <div
                  class="learn-progress__bar"
                  [style.width.%]="normalizedProgress(course.progress)"
                  role="progressbar"
                  [attr.aria-label]="course.course.title + ' progress'"
                  [attr.aria-valuenow]="normalizedProgress(course.progress)"
                  aria-valuemin="0"
                  aria-valuemax="100"
                ></div>
              </div>
            </div>
            <app-echo-button
              *ngIf="course.status !== 'completed'"
              color="secondary"
              [label]="getCourseActionLabel(course)"
              (click)="startCourse(course)"
            ></app-echo-button>
            <a [routerLink]="['/learn/courses', course.course_id]">Course path</a>
          </article>
        </div>
        <app-echo-state-panel
          *ngIf="!coursesLoading && !coursesLoadError && studentCourses.length === 0"
          variant="empty"
          eyebrow="No current courses"
          title="Your learning will appear here"
          body="When a teacher assigns a course or you enroll in available learning, it will appear here."
          actionLabel="Explore courses"
          (action)="goToCourses()"
        ></app-echo-state-panel>
      </section>

      <section class="learn-home__grid">
        <article class="learn-card" aria-labelledby="available-learning-heading">
          <div class="learn-card__heading">
            <div>
              <p class="learn-home__eyebrow">Available learning</p>
              <h2 id="available-learning-heading">Courses you can start</h2>
            </div>
            <a routerLink="/learn/products">Browse courses</a>
          </div>
          <app-echo-loading-state
            *ngIf="availableCoursesLoading || productsLoading"
            density="compact"
            ariaLabel="available-learning-loading"
            title="Loading available learning"
            body="We are checking courses and paths available to you."
          ></app-echo-loading-state>
          <app-echo-state-panel
            *ngIf="!availableCoursesLoading && availableCoursesLoadError"
            variant="error"
            [compact]="true"
            eyebrow="Catalog unavailable"
            title="We could not load available courses"
            [body]="availableCoursesLoadError"
            actionLabel="Retry"
            (action)="retryAvailableCoursesLoad()"
          ></app-echo-state-panel>
          <div *ngIf="!availableCoursesLoading && !productsLoading && !availableCoursesLoadError && availableLearningCount" class="learning-list learning-list--compact">
            <article class="learning-item" *ngFor="let course of visibleAvailableCourses">
              <div>
                <span class="learn-status">Available</span>
                <h3>{{ course.title }}</h3>
                <p>{{ course.description }}</p>
              </div>
              <app-echo-button color="accent" label="Start course" (click)="enrollInCourse(course.id)"></app-echo-button>
              <a [routerLink]="['/learn/courses', course.id]">View course</a>
            </article>
            <article class="learning-item" *ngFor="let product of visibleAvailableProducts">
              <div>
                <span class="learn-status">Available</span>
                <h3>{{ product.title }}</h3>
                <p>{{ product.description || product.learner_visibility }}</p>
              </div>
              <app-echo-button
                *ngIf="product.course_id"
                color="accent"
                label="Start course"
                (click)="enrollProduct(product)"
              ></app-echo-button>
              <a *ngIf="product.course_id" [routerLink]="['/learn/courses', product.course_id]">View course</a>
              <p *ngIf="!product.course_id" class="learn-card__copy">This resource is visible to you, but course lessons are not connected yet.</p>
            </article>
          </div>
          <app-echo-state-panel
            *ngIf="!availableCoursesLoading && !productsLoading && !availableCoursesLoadError && availableLearningCount === 0"
            variant="empty"
            [compact]="true"
            eyebrow="No additional courses"
            title="No available courses right now"
            body="Keep going with your current learning. New courses will appear here when they are ready for you."
          ></app-echo-state-panel>
        </article>

        <article class="learn-card" aria-labelledby="achievements-heading">
          <div class="learn-card__heading">
            <div>
              <p class="learn-home__eyebrow">Achievements</p>
              <h2 id="achievements-heading">Badges and certificates</h2>
            </div>
            <a routerLink="/learn/certificates">View all</a>
          </div>
          <app-echo-loading-state
            *ngIf="badgesLoading || certificationsLoading"
            density="compact"
            ariaLabel="achievements-loading"
            title="Loading achievements"
            body="We are restoring your badges and certificates."
          ></app-echo-loading-state>
          <div *ngIf="!badgesLoading && !certificationsLoading && earnedAchievementCount" class="achievement-list">
            <article *ngFor="let badge of studentBadges | slice:0:3">
              <img *ngIf="badge.badge?.image_url" [src]="badge.badge?.image_url" [alt]="badge.badge?.title || 'Earned badge'" />
              <div>
                <h3>{{ badge.badge?.title || 'Earned badge' }}</h3>
                <p>{{ badge.badge?.description || 'You earned this badge through your learning.' }}</p>
              </div>
            </article>
            <article *ngFor="let certificate of certifications | slice:0:2">
              <div class="achievement-list__icon" aria-hidden="true">✓</div>
              <div>
                <h3>{{ certificate.certification.title }}</h3>
                <p>Awarded {{ certificate.awarded_at | date:'mediumDate' }}</p>
              </div>
            </article>
          </div>
          <app-echo-state-panel
            *ngIf="!badgesLoading && !certificationsLoading && earnedAchievementCount === 0"
            variant="empty"
            [compact]="true"
            eyebrow="No achievements yet"
            title="Your achievements will appear here"
            body="Complete lessons, courses, and supported assessments to earn badges or certificates."
          ></app-echo-state-panel>
        </article>
      </section>
    </section>
  `,
  styles: [`
    .learn-home { color: var(--ee-text); display: grid; gap: var(--space-layout-section, 1.5rem); padding: clamp(1rem, 3vw, 2rem); }
    .learn-home__hero, .learn-card { background: var(--ee-surface); border: 1px solid var(--ee-border); border-radius: var(--ee-radius-lg, 8px); box-shadow: var(--ee-shadow-soft); padding: clamp(1rem, 3vw, 1.5rem); }
    .learn-home__hero { display: grid; gap: 1.25rem; }
    .learn-home__eyebrow { color: var(--ee-text-muted); font-size: .76rem; font-weight: 800; letter-spacing: .12em; margin: 0 0 .35rem; text-transform: uppercase; }
    h1, h2, h3, p { letter-spacing: 0; margin: 0; }
    h1 { font-size: clamp(2rem, 5vw, 3.35rem); line-height: 1.02; max-width: 12ch; }
    h2 { font-size: clamp(1.25rem, 3vw, 1.65rem); }
    h3 { font-size: 1rem; }
    a { color: var(--ee-action-primary); font-weight: 800; text-decoration: underline; text-underline-offset: .2em; }
    .learn-home__intro, .learn-card__copy, .learn-card__guidance, .learning-item p, .achievement-list p { color: var(--ee-text-soft); line-height: 1.6; }
    .learn-home__quick-nav { display: grid; gap: .65rem; grid-template-columns: repeat(auto-fit, minmax(9rem, 1fr)); }
    .learn-home__quick-nav a { align-items: center; background: var(--ee-surface-muted, #f8fafc); border: 1px solid var(--ee-border); border-radius: var(--ee-radius, 6px); color: var(--ee-text); display: inline-flex; justify-content: center; min-height: 44px; padding: .65rem .85rem; text-decoration: none; }
    .learn-home__grid { display: grid; gap: 1rem; grid-template-columns: minmax(0, 1.35fr) minmax(18rem, .65fr); }
    .learn-home__grid--top { align-items: stretch; }
    .learn-card { display: grid; gap: 1rem; min-width: 0; }
    .learn-card--priority { border-color: color-mix(in srgb, var(--ee-action-primary) 30%, var(--ee-border)); }
    .learn-card__heading { align-items: start; display: flex; gap: 1rem; justify-content: space-between; }
    .learn-card__secondary-action { justify-self: start; }
    .learn-card__title { color: var(--ee-text); font-size: clamp(1.25rem, 3vw, 1.75rem); font-weight: 800; }
    .learn-status { background: var(--ee-surface-muted, #f8fafc); border: 1px solid var(--ee-border); border-radius: 999px; color: var(--ee-text); display: inline-flex; font-size: .76rem; font-weight: 800; line-height: 1.2; padding: .35rem .65rem; white-space: nowrap; }
    .learn-summary { display: grid; gap: .75rem; grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .learn-summary div { background: var(--ee-surface-muted, #f8fafc); border: 1px solid var(--ee-border); border-radius: var(--ee-radius, 6px); padding: .85rem; }
    .learn-summary strong { display: block; font-size: 1.65rem; line-height: 1; }
    .learn-summary span, .learn-progress span { color: var(--ee-text-soft); font-size: .82rem; font-weight: 700; }
    .learn-progress { background: var(--ee-surface-muted, #f8fafc); border: 1px solid var(--ee-border); border-radius: var(--ee-radius, 6px); display: grid; gap: .65rem; padding: .85rem; }
    .learn-progress > div:first-child { align-items: center; display: flex; justify-content: space-between; }
    .learn-progress strong { color: var(--ee-action-primary); }
    .learn-progress__track { background: var(--ee-border); border-radius: 999px; height: .7rem; overflow: hidden; }
    .learn-progress__bar { background: var(--ee-action-primary); border-radius: inherit; height: 100%; min-width: .15rem; }
    .learn-progress--compact { padding: .65rem; }
    .learn-support { border: 1px solid var(--ee-border); border-radius: var(--ee-radius, 6px); display: grid; gap: .45rem; padding: .85rem; }
    .learn-support[data-support-state="remediation"] { background: var(--ee-status-warning-bg, #fef3c7); border-color: var(--ee-status-warning-border, #f59e0b); }
    .learn-support[data-support-state="enrichment"] { background: var(--ee-status-success-bg, #dcfce7); border-color: var(--ee-status-success-border, #22c55e); }
    .learn-support__label { color: var(--ee-text-muted); font-size: .72rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
    .learn-support__title { font-weight: 800; }
    .learn-support ul { margin: .25rem 0 0; padding-inline-start: 1.2rem; }
    .learning-list { display: grid; gap: .85rem; }
    .learning-list--compact { grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
    .learning-item { align-items: start; background: var(--ee-surface-muted, #f8fafc); border: 1px solid var(--ee-border); border-radius: var(--ee-radius, 6px); display: grid; gap: .85rem; grid-template-columns: minmax(0, 1fr) minmax(10rem, .35fr) auto; padding: 1rem; }
    .learning-list--compact .learning-item { grid-template-columns: 1fr; }
    .achievement-list { display: grid; gap: .75rem; }
    .achievement-list article { align-items: center; background: var(--ee-surface-muted, #f8fafc); border: 1px solid var(--ee-border); border-radius: var(--ee-radius, 6px); display: flex; gap: .75rem; padding: .85rem; }
    .achievement-list img, .achievement-list__icon { border-radius: 999px; height: 2.5rem; object-fit: cover; width: 2.5rem; }
    .achievement-list__icon { align-items: center; background: var(--ee-action-primary); color: var(--ee-action-primary-contrast, #fff); display: inline-flex; font-weight: 900; justify-content: center; }
    a:focus-visible, button:focus-visible { outline: 3px solid var(--ee-focus-ring); outline-offset: 3px; }
    @media (max-width: 900px) {
      .learn-home__grid, .learning-item { grid-template-columns: 1fr; }
      .learn-card__heading { display: grid; }
    }
    @media (max-width: 480px) {
      .learn-home { padding: .75rem; }
      .learn-summary { grid-template-columns: 1fr; }
      .learn-home__quick-nav { grid-template-columns: 1fr; }
    }
  `]
})
export class LearnerPortalComponent implements OnInit {
  private readonly analyticsService = inject(AnalyticsService);
  private readonly badgesService = inject(BadgesService);
  private readonly coursesService = inject(CoursesService);
  private readonly permissionsService = inject(PermissionsService);
  private readonly programsService = inject(ProgramsService);
  private readonly router = inject(Router);
  private readonly toastService = inject(ToastService);
  private readonly v2Platform = inject(V2PlatformService);

  studentCourses: StudentCourseWithDetails[] = [];
  activeStudentCourse?: StudentCourseWithDetails;
  activeStudentCourseReason = '';
  activeContinuationTitle = 'Your next lesson is ready';
  activeContinuationEyebrow = 'Selected continuation';
  activeContinuationState: ContinuationGuidance['support_state'] = 'normal';
  activeReinforcementMessage = '';
  activePrompts: string[] = [];
  availableCourses: Course[] = [];
  products: LearnerProduct[] = [];
  programs: Program[] = [];
  certifications: StudentCertification[] = [];
  studentBadges: StudentBadge[] = [];
  badgeProgress: StudentProgressResponse['badge_progress'] = [];
  lessonsCompleted = 0;
  coursesCompleted = 0;

  coursesLoading = true;
  coursesLoadError = '';
  availableCoursesLoading = true;
  availableCoursesLoadError = '';
  productsLoading = true;
  progressLoading = true;
  badgesLoading = true;
  certificationsLoading = true;

  get enrolledProducts(): LearnerProduct[] {
    return this.products.filter(product => product.is_enrolled);
  }

  get availableProducts(): LearnerProduct[] {
    return this.products.filter(product => !product.is_enrolled);
  }

  get visibleAvailableProducts(): LearnerProduct[] {
    return this.availableProducts.slice(0, 2);
  }

  get visibleAvailableCourses(): Course[] {
    return this.availableCourses.slice(0, Math.max(0, 4 - this.visibleAvailableProducts.length));
  }

  get availableLearningCount(): number {
    return this.availableCourses.length + this.availableProducts.length;
  }

  get inProgressCourseCount(): number {
    return this.studentCourses.filter(course => course.status !== 'completed').length;
  }

  get earnedAchievementCount(): number {
    return this.studentBadges.length + this.certifications.length;
  }

  get activeCourseProgress(): number {
    return this.normalizedProgress(this.activeStudentCourse?.progress);
  }

  get activeCourseStatusLabel(): string {
    if (!this.activeStudentCourse) {
      return '';
    }
    return this.statusLabel(this.activeStudentCourse.status, this.activeStudentCourse.progress);
  }

  get continuationTitle(): string {
    return this.activeStudentCourse?.course.title || 'No active lesson yet';
  }

  get noContinuationTitle(): string {
    if (this.studentCourses.length && this.studentCourses.every(course => course.status === 'completed')) {
      return 'You completed your current learning';
    }
    return 'Your next lesson will appear here';
  }

  get noContinuationBody(): string {
    if (this.studentCourses.length && this.studentCourses.every(course => course.status === 'completed')) {
      return 'You finished your current courses. Review your achievements or explore another course when you are ready.';
    }
    return 'When a course is assigned or you start a course, your next learning step will appear here.';
  }

  ngOnInit(): void {
    this.loadStudentCourses();
    this.loadAvailableProducts();
    this.loadProgress();
    this.loadBadges();
    this.loadProgramsAndCertifications();
  }

  loadStudentCourses(): void {
    this.coursesLoading = true;
    this.coursesLoadError = '';
    this.coursesService.getStudentCourses().subscribe({
      next: courses => {
        this.studentCourses = courses;
        this.resolveContinuationCourse();
        this.studentCourses.forEach(course => {
          this.coursesService.getCourseProgress(course).subscribe(progress => {
            course.progress = progress;
            if (this.activeStudentCourse?.id === course.id) {
              this.activeStudentCourse.progress = progress;
            }
          });
        });
        this.loadAvailableCourses();
        this.coursesLoading = false;
      },
      error: () => {
        this.studentCourses = [];
        this.activeStudentCourse = undefined;
        this.availableCourses = [];
        this.availableCoursesLoading = false;
        this.coursesLoadError = 'We could not load your courses. No progress was changed. Try again when your connection is ready.';
        this.coursesLoading = false;
      },
    });
  }

  loadAvailableCourses(): void {
    this.availableCoursesLoading = true;
    this.availableCoursesLoadError = '';
    this.coursesService.getCourses().subscribe({
      next: courses => {
        const enrolledCourseIds = new Set(this.studentCourses.map(course => course.course_id));
        this.availableCourses = courses.filter(course => !enrolledCourseIds.has(course.id));
        this.availableCoursesLoading = false;
      },
      error: () => {
        this.availableCourses = [];
        this.availableCoursesLoadError = 'We could not load the course catalog. Your current learning is unchanged.';
        this.availableCoursesLoading = false;
      },
    });
  }

  loadAvailableProducts(): void {
    this.productsLoading = true;
    this.v2Platform.getLearnerProducts().subscribe({
      next: products => {
        this.products = products;
        this.productsLoading = false;
      },
      error: () => {
        this.products = [];
        this.productsLoading = false;
      },
    });
  }

  loadProgress(): void {
    this.progressLoading = true;
    this.analyticsService.getStudentProgress().subscribe({
      next: progress => {
        this.badgeProgress = progress.badge_progress;
        this.lessonsCompleted = progress.metrics.lessons_completed;
        this.coursesCompleted = progress.metrics.courses_completed;
        this.progressLoading = false;
      },
      error: () => {
        this.badgeProgress = [];
        this.progressLoading = false;
      },
    });
  }

  loadBadges(): void {
    this.permissionsService.user$.pipe(take(1)).subscribe(user => {
      const userId = user?.user_id;
      if (!userId) {
        this.badgesLoading = false;
        return;
      }
      this.badgesLoading = true;
      this.badgesService.getStudentBadges(userId).subscribe({
        next: badges => {
          this.studentBadges = badges;
          this.badgesLoading = false;
        },
        error: () => {
          this.studentBadges = [];
          this.badgesLoading = false;
        },
      });
    });
  }

  loadProgramsAndCertifications(): void {
    this.programsService.getPrograms().subscribe({
      next: programs => this.programs = programs,
      error: () => this.programs = [],
    });

    this.certificationsLoading = true;
    this.programsService.getMyCertifications().subscribe({
      next: certifications => {
        this.certifications = certifications;
        this.certificationsLoading = false;
      },
      error: () => {
        this.certifications = [];
        this.certificationsLoading = false;
      },
    });
  }

  startCourse(course: StudentCourseWithDetails): void {
    this.coursesService.startCourse({ course_id: course.course_id || course.course.id }).subscribe({
      next: segment => {
        if (segment.delivery_state === 'governed_available' && segment.unit_progress_id) {
          this.router.navigate(['/learn/lesson', segment.unit_progress_id]);
          return;
        }
        this.toastService.show(segment.detail || 'This lesson is not ready yet. Try again later.', 'error');
      },
      error: () => this.toastService.show('We could not start this lesson. Try again in a moment.', 'error'),
    });
  }

  enrollInCourse(courseId: string): void {
    this.coursesService.enrollInCourse(courseId).subscribe({
      next: () => {
        this.toastService.show('Course added to your learning.', 'success');
        this.loadStudentCourses();
      },
      error: () => this.toastService.show('We could not add this course. You may already have it.', 'error'),
    });
  }

  enrollProduct(product: LearnerProduct): void {
    if (!product.course_id) {
      this.toastService.show('This learning item is not connected to course lessons yet.', 'error');
      return;
    }
    this.enrollInCourse(product.course_id);
  }

  retryCourseLoad(): void {
    this.loadStudentCourses();
  }

  retryAvailableCoursesLoad(): void {
    this.loadAvailableCourses();
    this.loadAvailableProducts();
  }

  goToCourses(): void {
    this.router.navigate(['/learn/products']);
  }

  getCourseActionLabel(course: StudentCourseWithDetails): string {
    return (course.progress ?? 0) > 0 || course.status === 'active' || course.status === 'in_progress'
      ? 'Resume lesson'
      : 'Start lesson';
  }

  normalizedProgress(value: number | undefined): number {
    return Math.max(0, Math.min(100, value || 0));
  }

  statusLabel(status: string | undefined, progress: number | undefined): string {
    if (status === 'completed') {
      return 'Complete';
    }
    if (this.normalizedProgress(progress) > 0 || status === 'active' || status === 'in_progress') {
      return 'In progress';
    }
    return 'Ready';
  }

  private resolveContinuationCourse(): void {
    const inProgressStatuses = new Set(['active', 'in_progress', 'in-progress']);
    const orderedCourses = [...this.studentCourses].sort((left, right) => {
      const leftDate = Date.parse(left.enrolled_on || '') || 0;
      const rightDate = Date.parse(right.enrolled_on || '') || 0;
      if (leftDate !== rightDate) {
        return leftDate - rightDate;
      }
      return left.course.title.localeCompare(right.course.title);
    });

    this.activeStudentCourse = orderedCourses.find(course =>
      course.status !== 'completed'
      && (inProgressStatuses.has((course.status || '').toLowerCase()) || (course.progress ?? 0) > 0)
    ) || orderedCourses.find(course => course.status !== 'completed');

    this.applyContinuationGuidance(this.activeStudentCourse?.continuation_guidance);
  }

  private applyContinuationGuidance(guidance: ContinuationGuidance | null | undefined): void {
    this.activeStudentCourseReason = guidance?.learner_message || 'Continue from the next approved lesson in this course.';
    this.activeContinuationTitle = guidance?.learner_title || 'Your next lesson is ready';
    this.activeContinuationState = guidance?.support_state || 'normal';
    this.activeReinforcementMessage = guidance?.reinforcement_message || '';
    this.activePrompts =
      guidance?.support_state === 'remediation'
        ? guidance.review_prompts || []
        : guidance?.support_state === 'enrichment'
          ? guidance.extension_prompts || []
          : [];
    this.activeContinuationEyebrow =
      guidance?.support_state === 'remediation'
        ? 'Helpful review'
        : guidance?.support_state === 'enrichment'
          ? 'Optional deeper learning'
          : 'Recommended next step';
  }
}
