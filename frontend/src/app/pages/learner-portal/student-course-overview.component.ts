import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { forkJoin, of } from 'rxjs';
import { catchError, finalize } from 'rxjs/operators';

import {
  StudentCurriculumComponent,
  StudentCurriculumLesson,
  StudentCurriculumUnit,
} from '../../components/student-curriculum/student-curriculum.component';
import { EchoButtonComponent } from '../../components/echo-button/echo-button.component';
import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { Course } from '../../models/course';
import { Lesson } from '../../models/lesson';
import { SegmentResponse } from '../../models/segment-response.model';
import { StudentCourseWithDetails } from '../../models/student-course-with-details.model';
import { Unit } from '../../models/unit';
import { CoursesService } from '../../services/courses.service';
import { ToastService } from '../../services/toast.service';

@Component({
  selector: 'app-student-course-overview',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    StudentCurriculumComponent,
    EchoButtonComponent,
    EchoLoadingStateComponent,
    EchoStatePanelComponent,
  ],
  template: `
    <section class="student-course" aria-labelledby="student-course-title">
      <a routerLink="/learn" class="student-course__back">Back to Learn</a>

      <app-echo-loading-state
        *ngIf="loading"
        density="page"
        ariaLabel="course-overview-loading"
        title="Preparing course overview"
        body="We are loading the course path and your current learning state."
      ></app-echo-loading-state>

      <app-echo-state-panel
        *ngIf="!loading && loadErrorMessage"
        variant="error"
        eyebrow="Course unavailable"
        title="We could not load this course"
        [body]="loadErrorMessage"
        actionLabel="Retry"
        actionAriaLabel="Retry loading this course"
        (action)="loadCourse()"
      ></app-echo-state-panel>

      <ng-container *ngIf="!loading && !loadErrorMessage && course">
        <header class="student-course__hero">
          <div class="student-course__identity">
            <p class="student-course__eyebrow">Course</p>
            <h1 id="student-course-title">{{ course.title }}</h1>
            <p class="student-course__description">
              {{ course.description || 'This course is ready for student learning.' }}
            </p>
            <div class="student-course__tags" aria-label="Course context">
              <span>{{ enrollmentLabel }}</span>
              <span *ngIf="lessonCount">{{ lessonCount }} lesson{{ lessonCount === 1 ? '' : 's' }}</span>
              <span *ngIf="unitCount">{{ unitCount }} unit{{ unitCount === 1 ? '' : 's' }}</span>
            </div>
          </div>

          <aside class="student-course__action" aria-labelledby="course-action-heading">
            <p class="student-course__eyebrow">Next step</p>
            <h2 id="course-action-heading">{{ primaryActionTitle }}</h2>
            <p>{{ primaryActionBody }}</p>
            <div class="student-course__progress" aria-labelledby="course-progress-label">
              <div>
                <span id="course-progress-label">Course progress</span>
                <strong>{{ courseProgress | number:'1.0-0' }}%</strong>
              </div>
              <div class="student-course__track">
                <div
                  class="student-course__bar"
                  role="progressbar"
                  aria-label="Course progress"
                  aria-valuemin="0"
                  aria-valuemax="100"
                  [attr.aria-valuenow]="courseProgress"
                  [style.width.%]="courseProgress"
                ></div>
              </div>
            </div>
            <app-echo-button
              color="primary"
              [label]="primaryActionLabel"
              [disabled]="actionPending || primaryActionDisabled"
              [ariaLabel]="primaryActionAriaLabel"
              (click)="performPrimaryAction()"
            ></app-echo-button>
            <p *ngIf="actionMessage" class="student-course__action-message" role="status" aria-live="polite">
              {{ actionMessage }}
            </p>
          </aside>
        </header>

        <section *ngIf="learningObjectives" class="student-course__section" aria-labelledby="course-goals-heading">
          <p class="student-course__eyebrow">Learning goals</p>
          <h2 id="course-goals-heading">What this course helps you learn</h2>
          <p>{{ learningObjectives }}</p>
        </section>

        <app-student-curriculum
          [units]="curriculumUnits"
          [summaryLabel]="curriculumSummaryLabel"
          (openLesson)="openCurriculumLesson($event)"
        ></app-student-curriculum>

        <section class="student-course__section" aria-labelledby="course-outcome-heading">
          <p class="student-course__eyebrow">Completion outcome</p>
          <h2 id="course-outcome-heading">When you finish</h2>
          <p>
            EchoEd will use the existing course progress, assessment, badge, and certificate systems to record supported milestones.
            Any badges or certificates you earn appear in Achievements.
          </p>
          <a routerLink="/learn/certificates">View achievements and certificates</a>
        </section>
      </ng-container>
    </section>
  `,
  styles: [`
    .student-course {
      color: var(--ee-text);
      display: grid;
      gap: var(--ee-space-5, 1.25rem);
      padding: clamp(1rem, 3vw, 2rem);
    }

    .student-course__back,
    .student-course__section a {
      color: var(--ee-action-primary);
      font-weight: 900;
      text-decoration: underline;
      text-underline-offset: 0.2em;
    }

    .student-course__hero,
    .student-course__section {
      background: var(--ee-surface);
      border: 1px solid var(--ee-border);
      border-radius: var(--ee-radius-lg, 8px);
      box-shadow: var(--ee-shadow-soft);
      padding: clamp(1rem, 3vw, 1.5rem);
    }

    .student-course__hero {
      display: grid;
      gap: clamp(1rem, 3vw, 1.5rem);
      grid-template-columns: minmax(0, 1fr) minmax(18rem, 0.38fr);
    }

    .student-course__identity,
    .student-course__section,
    .student-course__action {
      display: grid;
      gap: 0.8rem;
    }

    .student-course__action {
      align-content: start;
      background: var(--ee-surface-muted, #f8fafc);
      border: 1px solid var(--ee-border);
      border-radius: var(--ee-radius, 6px);
      padding: 1rem;
    }

    .student-course__eyebrow {
      color: var(--ee-text-muted);
      font-size: 0.76rem;
      font-weight: 900;
      letter-spacing: 0.12em;
      margin: 0;
      text-transform: uppercase;
    }

    h1,
    h2,
    p {
      letter-spacing: 0;
      margin: 0;
    }

    h1 {
      font-size: clamp(2.1rem, 6vw, 4rem);
      line-height: 1;
      max-width: 13ch;
    }

    h2 {
      font-size: clamp(1.2rem, 3vw, 1.6rem);
    }

    .student-course__description,
    .student-course__section p,
    .student-course__action p,
    .student-course__action-message {
      color: var(--ee-text-soft);
      line-height: 1.65;
    }

    .student-course__tags {
      display: flex;
      flex-wrap: wrap;
      gap: 0.55rem;
    }

    .student-course__tags span {
      background: var(--ee-surface-muted, #f8fafc);
      border: 1px solid var(--ee-border);
      border-radius: 999px;
      display: inline-flex;
      font-size: 0.8rem;
      font-weight: 900;
      padding: 0.35rem 0.65rem;
    }

    .student-course__progress {
      display: grid;
      gap: 0.55rem;
    }

    .student-course__progress > div:first-child {
      align-items: center;
      display: flex;
      justify-content: space-between;
    }

    .student-course__progress span {
      color: var(--ee-text-soft);
      font-size: 0.82rem;
      font-weight: 800;
    }

    .student-course__progress strong {
      color: var(--ee-action-primary);
    }

    .student-course__track {
      background: var(--ee-border);
      border-radius: 999px;
      height: 0.72rem;
      overflow: hidden;
    }

    .student-course__bar {
      background: var(--ee-action-primary);
      border-radius: inherit;
      height: 100%;
      min-width: 0.15rem;
    }

    @media (max-width: 900px) {
      .student-course__hero {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 480px) {
      .student-course {
        padding: 0.75rem;
      }
    }
  `],
})
export class StudentCourseOverviewComponent implements OnInit {
  private readonly coursesService = inject(CoursesService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly toastService = inject(ToastService);

  courseId = '';
  course?: Course;
  enrolledCourse?: StudentCourseWithDetails;
  currentSegment?: SegmentResponse;
  loading = true;
  loadErrorMessage = '';
  actionPending = false;
  actionMessage = '';
  courseProgress = 0;
  curriculumUnits: StudentCurriculumUnit[] = [];

  get unitCount(): number {
    return this.orderedUnits.length;
  }

  get lessonCount(): number {
    return this.orderedUnits.reduce((count, unit) => count + this.orderedLessons(unit).length, 0);
  }

  get learningObjectives(): string {
    return this.course?.learning_objectives || '';
  }

  get enrollmentLabel(): string {
    if (!this.enrolledCourse) {
      return 'Available to start';
    }
    if (this.enrolledCourse.status === 'completed') {
      return 'Completed';
    }
    return this.courseProgress > 0 ? 'In progress' : 'Ready';
  }

  get primaryActionLabel(): string {
    if (this.actionPending) {
      return 'Preparing...';
    }
    if (!this.enrolledCourse) {
      return 'Start course';
    }
    if (this.enrolledCourse.status === 'completed') {
      return 'Review course';
    }
    if (this.currentSegment?.delivery_state === 'governed_available') {
      return this.courseProgress > 0 ? 'Resume lesson' : 'Start lesson';
    }
    return 'Check course status';
  }

  get primaryActionTitle(): string {
    if (!this.enrolledCourse) {
      return 'Start when you are ready';
    }
    if (this.enrolledCourse.status === 'completed') {
      return 'Course completed';
    }
    if (this.currentSegment?.delivery_state === 'governed_available') {
      return 'Your next lesson is ready';
    }
    return 'Course status';
  }

  get primaryActionBody(): string {
    if (!this.enrolledCourse) {
      return 'Starting adds this course to your learning and opens the next governed lesson when available.';
    }
    if (this.enrolledCourse.status === 'completed') {
      return 'Review the course path and visit Achievements to see supported badges or certificates.';
    }
    if (this.currentSegment?.delivery_state === 'governed_available') {
      return 'Continue through the next approved lesson in your course path.';
    }
    return this.currentSegment?.detail || 'The next lesson is not available for learner delivery right now.';
  }

  get primaryActionAriaLabel(): string {
    return `${this.primaryActionLabel}: ${this.course?.title || 'course'}`;
  }

  get primaryActionDisabled(): boolean {
    return this.enrolledCourse?.status === 'completed' ? false : false;
  }

  get curriculumSummaryLabel(): string {
    if (!this.lessonCount) {
      return 'No learner lessons listed';
    }
    return `${this.unitCount} unit${this.unitCount === 1 ? '' : 's'}, ${this.lessonCount} lesson${this.lessonCount === 1 ? '' : 's'}`;
  }

  private get orderedUnits(): Unit[] {
    return [...(this.course?.units || [])].sort((left, right) => {
      const leftOrder = left.order ?? Number.MAX_SAFE_INTEGER;
      const rightOrder = right.order ?? Number.MAX_SAFE_INTEGER;
      if (leftOrder !== rightOrder) {
        return leftOrder - rightOrder;
      }
      return left.title.localeCompare(right.title);
    });
  }

  ngOnInit(): void {
    this.courseId = this.route.snapshot.paramMap.get('courseId') || '';
    this.loadCourse();
  }

  loadCourse(): void {
    if (!this.courseId) {
      this.loading = false;
      this.loadErrorMessage = 'This course link is missing a course id.';
      return;
    }

    this.loading = true;
    this.loadErrorMessage = '';
    this.actionMessage = '';

    forkJoin({
      course: this.coursesService.getCourseById(this.courseId),
      studentCourses: this.coursesService.getStudentCourses().pipe(catchError(() => of([] as StudentCourseWithDetails[]))),
    }).subscribe({
      next: ({ course, studentCourses }) => {
        this.course = course as unknown as Course;
        this.enrolledCourse = studentCourses.find(studentCourse => studentCourse.course_id === this.courseId);
        this.courseProgress = 0;
        this.currentSegment = undefined;
        this.curriculumUnits = this.buildCurriculumUnits();

        if (!this.enrolledCourse) {
          this.loading = false;
          return;
        }

        forkJoin({
          progress: this.coursesService.getCourseProgress(this.enrolledCourse),
          segment: this.enrolledCourse.unit_progress_id
            ? this.coursesService.getCurrentSegment(this.enrolledCourse.unit_progress_id).pipe(catchError(() => of(undefined)))
            : of(undefined),
        }).subscribe({
          next: ({ progress, segment }) => {
            this.courseProgress = this.normalizeProgress(progress);
            this.currentSegment = segment;
            this.curriculumUnits = this.buildCurriculumUnits();
            this.loading = false;
          },
          error: () => {
            this.curriculumUnits = this.buildCurriculumUnits();
            this.loading = false;
          },
        });
      },
      error: (error) => {
        this.course = undefined;
        this.enrolledCourse = undefined;
        this.currentSegment = undefined;
        this.curriculumUnits = [];
        this.loading = false;
        this.loadErrorMessage = error?.status === 400
          ? 'This course link is not valid.'
          : error?.status === 404
            ? 'This course could not be found.'
            : 'We could not load this course. Your progress was not changed.';
      },
    });
  }

  performPrimaryAction(): void {
    if (!this.course) {
      return;
    }

    if (this.enrolledCourse?.status === 'completed') {
      this.actionMessage = 'This course is complete. Review the course path below or open Achievements.';
      return;
    }

    if (!this.enrolledCourse) {
      this.actionPending = true;
      this.actionMessage = 'Adding this course to your learning...';
      this.coursesService.enrollInCourse(this.course.id).subscribe({
        next: () => {
          this.actionMessage = 'Course added. Preparing your first lesson...';
          this.loadAndStartEnrolledCourse();
        },
        error: () => {
          this.actionPending = false;
          this.actionMessage = 'We could not add this course. It may already be in your learning.';
          this.toastService.show('Unable to add this course right now.', 'error');
        },
      });
      return;
    }

    this.startEnrolledCourse(this.enrolledCourse);
  }

  openCurriculumLesson(lesson: StudentCurriculumLesson): void {
    if (!lesson.canOpen || !this.enrolledCourse) {
      this.actionMessage = lesson.stateDescription;
      return;
    }
    this.startEnrolledCourse(this.enrolledCourse);
  }

  private loadAndStartEnrolledCourse(): void {
    this.coursesService.getStudentCourses().subscribe({
      next: courses => {
        this.enrolledCourse = courses.find(course => course.course_id === this.courseId);
        if (!this.enrolledCourse) {
          this.actionPending = false;
          this.actionMessage = 'The course was added, but we could not find the new learning record yet. Return to Learn and try again.';
          return;
        }
        this.startEnrolledCourse(this.enrolledCourse);
      },
      error: () => {
        this.actionPending = false;
        this.actionMessage = 'The course was added, but we could not refresh the learning record.';
      },
    });
  }

  private startEnrolledCourse(course: StudentCourseWithDetails): void {
    this.actionPending = true;
    this.actionMessage = 'Preparing your governed lesson...';
    this.coursesService.startCourse({ course_id: course.course_id || course.course.id }).pipe(
      finalize(() => {
        this.actionPending = false;
      }),
    ).subscribe({
      next: segment => {
        if (segment.delivery_state === 'governed_available' && segment.unit_progress_id) {
          this.router.navigate(['/learn/lesson', segment.unit_progress_id]);
          return;
        }
        this.currentSegment = segment;
        this.curriculumUnits = this.buildCurriculumUnits();
        this.actionMessage = segment.detail || 'This course does not have a learner-ready lesson right now.';
      },
      error: error => {
        this.actionMessage = error?.error?.detail || 'We could not start this course right now. Try again in a moment.';
        this.toastService.show('Unable to start this course right now.', 'error');
      },
    });
  }

  private buildCurriculumUnits(): StudentCurriculumUnit[] {
    return this.orderedUnits.map(unit => {
      const lessons = this.orderedLessons(unit).map(lesson => this.mapLesson(lesson));
      const currentLessonCount = lessons.filter(lesson => lesson.state === 'current').length;
      const completedLessonCount = lessons.filter(lesson => lesson.state === 'complete').length;
      const progressLabel = this.enrolledCourse?.status === 'completed'
        ? `${lessons.length} of ${lessons.length} complete`
        : currentLessonCount
          ? 'Current unit'
          : completedLessonCount
            ? `${completedLessonCount} complete`
            : 'Included in course';

      return {
        id: unit.id,
        title: unit.title,
        order: unit.order,
        progressLabel,
        lessons,
      };
    });
  }

  private mapLesson(lesson: Lesson): StudentCurriculumLesson {
    if (this.enrolledCourse?.status === 'completed') {
      return this.lessonState(lesson, 'complete', 'Complete', 'This lesson is part of your completed course.', false);
    }

    if (!this.enrolledCourse) {
      return this.lessonState(lesson, 'included', 'Included', 'Start the course to open the next governed lesson.', false);
    }

    if (this.currentSegment?.delivery_state === 'governed_available' && this.currentSegment.lesson_id === lesson.id) {
      return this.lessonState(lesson, 'current', this.courseProgress > 0 ? 'In progress' : 'Up next', 'This is the next governed lesson available to you.', true);
    }

    if (this.currentSegment?.delivery_state && this.currentSegment.delivery_state !== 'governed_available') {
      return this.lessonState(lesson, 'unavailable', 'Unavailable', this.currentSegment.detail || 'This lesson path is not available right now.', false);
    }

    return this.lessonState(lesson, 'locked', 'Locked', 'Use the course action to open the next lesson when it becomes available.', false);
  }

  private lessonState(
    lesson: Lesson,
    state: StudentCurriculumLesson['state'],
    stateLabel: string,
    stateDescription: string,
    canOpen: boolean,
  ): StudentCurriculumLesson {
    return {
      id: lesson.id,
      title: lesson.title,
      objective: lesson.objective || lesson.learning_objectives,
      durationMinutes: lesson.duration_minutes,
      activityCount: lesson.activities?.length || 0,
      state,
      stateLabel,
      stateDescription,
      canOpen,
    };
  }

  private orderedLessons(unit: Unit): Lesson[] {
    return [...(unit.lessons || [])].sort((left, right) => {
      const leftOrder = left.order ?? Number.MAX_SAFE_INTEGER;
      const rightOrder = right.order ?? Number.MAX_SAFE_INTEGER;
      if (leftOrder !== rightOrder) {
        return leftOrder - rightOrder;
      }
      return left.title.localeCompare(right.title);
    });
  }

  private normalizeProgress(progress: number | undefined): number {
    return Math.max(0, Math.min(100, progress || 0));
  }
}
