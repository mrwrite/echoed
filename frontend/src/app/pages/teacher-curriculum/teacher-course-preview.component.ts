import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';

import {
  StudentCurriculumComponent,
  StudentCurriculumLesson,
  StudentCurriculumUnit,
} from '../../components/student-curriculum/student-curriculum.component';
import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { Course } from '../../models/course';
import { Lesson } from '../../models/lesson';
import { Unit } from '../../models/unit';
import { CoursesService } from '../../services/courses.service';

@Component({
  selector: 'app-teacher-course-preview',
  standalone: true,
  imports: [CommonModule, RouterLink, StudentCurriculumComponent, EchoLoadingStateComponent, EchoStatePanelComponent],
  template: `
    <section class="teacher-preview" aria-labelledby="teacher-preview-title">
      <a routerLink="/teach/curriculum" class="teacher-preview__back">Back to curriculum</a>

      <app-echo-loading-state
        *ngIf="loading"
        density="page"
        ariaLabel="teacher-course-preview-loading"
        title="Loading course preview"
        body="We are loading course structure without starting a learner session."
      ></app-echo-loading-state>
      <app-echo-state-panel
        *ngIf="!loading && loadError"
        variant="error"
        eyebrow="Preview unavailable"
        title="We could not load this course preview"
        [body]="loadError"
        actionLabel="Retry"
        (action)="loadCourse()"
      ></app-echo-state-panel>

      <ng-container *ngIf="!loading && !loadError && course">
        <header class="teacher-preview__header">
          <div>
            <p class="teacher-preview__eyebrow">Teacher preview mode</p>
            <h1 id="teacher-preview-title">{{ course.title }}</h1>
            <p>{{ course.description || 'No course description available.' }}</p>
          </div>
          <aside aria-labelledby="preview-mode-heading">
            <h2 id="preview-mode-heading">Preview only</h2>
            <p>No learner enrollment, lesson session, or progress record will be created from this page.</p>
          </aside>
        </header>

        <section class="teacher-preview__panel" aria-labelledby="preview-purpose-heading">
          <p class="teacher-preview__eyebrow">Course purpose</p>
          <h2 id="preview-purpose-heading">What learners will see</h2>
          <p>{{ course.learning_objectives || 'Learning objectives are not available from the current course data.' }}</p>
          <dl>
            <div>
              <dt>Units</dt>
              <dd>{{ unitCount }}</dd>
            </div>
            <div>
              <dt>Lessons</dt>
              <dd>{{ lessonCount }}</dd>
            </div>
          </dl>
        </section>

        <app-student-curriculum
          [units]="curriculumUnits"
          [summaryLabel]="curriculumSummaryLabel"
          (openLesson)="notePreviewOnly($event)"
        ></app-student-curriculum>

        <section class="teacher-preview__panel" aria-labelledby="preview-assessment-heading">
          <p class="teacher-preview__eyebrow">Assessments and resources</p>
          <h2 id="preview-assessment-heading">Supported preview detail</h2>
          <p>
            Lesson activities, discussion prompts, teacher notes, sources, and assessment references appear where they are included in the current course and lesson payloads.
            This page does not call the student start-course API.
          </p>
          <p *ngIf="previewMessage" role="status" aria-live="polite">{{ previewMessage }}</p>
        </section>
      </ng-container>
    </section>
  `,
  styleUrl: './teacher-course-preview.component.scss',
})
export class TeacherCoursePreviewComponent implements OnInit {
  courseId = '';
  course?: Course;
  loading = true;
  loadError = '';
  previewMessage = '';
  curriculumUnits: StudentCurriculumUnit[] = [];

  constructor(
    private route: ActivatedRoute,
    private coursesService: CoursesService,
  ) {}

  ngOnInit(): void {
    this.courseId = this.route.snapshot.paramMap.get('courseId') || '';
    this.loadCourse();
  }

  get unitCount(): number {
    return this.orderedUnits.length;
  }

  get lessonCount(): number {
    return this.orderedUnits.reduce((count, unit) => count + this.orderedLessons(unit).length, 0);
  }

  get curriculumSummaryLabel(): string {
    return `${this.unitCount} unit${this.unitCount === 1 ? '' : 's'}, ${this.lessonCount} lesson${this.lessonCount === 1 ? '' : 's'} in preview`;
  }

  loadCourse(): void {
    if (!this.courseId) {
      this.loading = false;
      this.loadError = 'This preview link is missing a course id.';
      return;
    }
    this.loading = true;
    this.loadError = '';
    this.previewMessage = '';
    this.coursesService.getCourseById(this.courseId).subscribe({
      next: (course) => {
        this.course = course as unknown as Course;
        this.curriculumUnits = this.buildCurriculumUnits();
        this.loading = false;
      },
      error: (error) => {
        this.course = undefined;
        this.curriculumUnits = [];
        this.loading = false;
        this.loadError = error?.status === 404
          ? 'This course could not be found.'
          : 'We could not load the course preview. No learner progress was changed.';
      },
    });
  }

  notePreviewOnly(lesson: StudentCurriculumLesson): void {
    this.previewMessage = `${lesson.title} is shown in teacher preview only. Open the lesson runtime only through supported learner or staff lesson routes.`;
  }

  private get orderedUnits(): Unit[] {
    return [...(this.course?.units || [])].sort((left, right) => {
      const leftOrder = left.order ?? Number.MAX_SAFE_INTEGER;
      const rightOrder = right.order ?? Number.MAX_SAFE_INTEGER;
      return leftOrder === rightOrder ? left.title.localeCompare(right.title) : leftOrder - rightOrder;
    });
  }

  private buildCurriculumUnits(): StudentCurriculumUnit[] {
    return this.orderedUnits.map((unit, index) => ({
      id: unit.id,
      title: unit.title,
      order: unit.order ?? index + 1,
      progressLabel: 'Preview',
      lessons: this.orderedLessons(unit).map(lesson => this.mapLesson(lesson)),
    }));
  }

  private mapLesson(lesson: Lesson): StudentCurriculumLesson {
    return {
      id: lesson.id,
      title: lesson.title,
      objective: lesson.objective || lesson.learning_objectives,
      durationMinutes: lesson.duration_minutes,
      activityCount: lesson.activities?.length || 0,
      state: 'included',
      stateLabel: 'Preview',
      stateDescription: 'Teacher preview only. No learner progress will be recorded.',
      canOpen: true,
    };
  }

  private orderedLessons(unit: Unit): Lesson[] {
    return [...(unit.lessons || [])].sort((left, right) => {
      const leftOrder = left.order ?? Number.MAX_SAFE_INTEGER;
      const rightOrder = right.order ?? Number.MAX_SAFE_INTEGER;
      return leftOrder === rightOrder ? left.title.localeCompare(right.title) : leftOrder - rightOrder;
    });
  }
}
