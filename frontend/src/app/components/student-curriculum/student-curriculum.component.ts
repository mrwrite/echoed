import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

export type StudentLessonState = 'included' | 'current' | 'complete' | 'locked' | 'unavailable';

export interface StudentCurriculumLesson {
  id: string;
  title: string;
  objective?: string;
  durationMinutes?: number;
  activityCount: number;
  state: StudentLessonState;
  stateLabel: string;
  stateDescription: string;
  canOpen: boolean;
}

export interface StudentCurriculumUnit {
  id: string;
  title: string;
  order?: number;
  progressLabel: string;
  lessons: StudentCurriculumLesson[];
}

@Component({
  selector: 'app-student-curriculum',
  standalone: true,
  imports: [CommonModule],
  template: `
    <section class="student-curriculum" aria-labelledby="student-curriculum-heading">
      <div class="student-curriculum__header">
        <div>
          <p class="student-curriculum__eyebrow">Course path</p>
          <h2 id="student-curriculum-heading">Units and lessons</h2>
        </div>
        <p>{{ summaryLabel }}</p>
      </div>

      <ol *ngIf="units.length; else emptyCurriculum" class="student-curriculum__units">
        <li *ngFor="let unit of units; let unitIndex = index" class="student-curriculum__unit">
          <header>
            <div>
              <p class="student-curriculum__eyebrow">Unit {{ unitIndex + 1 }}</p>
              <h3>{{ unit.title }}</h3>
            </div>
            <span class="student-curriculum__unit-progress">{{ unit.progressLabel }}</span>
          </header>

          <ol class="student-curriculum__lessons">
            <li *ngFor="let lesson of unit.lessons; let lessonIndex = index">
              <button
                type="button"
                class="student-curriculum__lesson"
                [class.student-curriculum__lesson--current]="lesson.state === 'current'"
                [class.student-curriculum__lesson--complete]="lesson.state === 'complete'"
                [class.student-curriculum__lesson--locked]="lesson.state === 'locked' || lesson.state === 'unavailable'"
                [disabled]="!lesson.canOpen"
                [attr.aria-describedby]="'lesson-state-' + lesson.id"
                (click)="openLesson.emit(lesson)"
              >
                <span class="student-curriculum__lesson-index" aria-hidden="true">{{ lessonIndex + 1 }}</span>
                <span class="student-curriculum__lesson-main">
                  <span class="student-curriculum__lesson-title">{{ lesson.title }}</span>
                  <span *ngIf="lesson.objective" class="student-curriculum__lesson-objective">{{ lesson.objective }}</span>
                  <span class="student-curriculum__lesson-meta">
                    <span *ngIf="lesson.durationMinutes">{{ lesson.durationMinutes }} min</span>
                    <span>{{ lesson.activityCount }} activit{{ lesson.activityCount === 1 ? 'y' : 'ies' }}</span>
                  </span>
                </span>
                <span class="student-curriculum__state" [attr.data-state]="lesson.state">
                  <span>{{ lesson.stateLabel }}</span>
                  <small [id]="'lesson-state-' + lesson.id">{{ lesson.stateDescription }}</small>
                </span>
              </button>
            </li>
          </ol>
        </li>
      </ol>

      <ng-template #emptyCurriculum>
        <div class="student-curriculum__empty" role="status">
          <h3>No lessons are listed yet</h3>
          <p>This course does not have a learner-ready curriculum hierarchy available from the current course data.</p>
        </div>
      </ng-template>
    </section>
  `,
  styles: [`
    .student-curriculum {
      background: var(--ee-surface);
      border: 1px solid var(--ee-border);
      border-radius: var(--ee-radius-lg, 8px);
      box-shadow: var(--ee-shadow-soft);
      display: grid;
      gap: var(--ee-space-4, 1rem);
      padding: clamp(1rem, 3vw, 1.5rem);
    }

    .student-curriculum__header,
    .student-curriculum__unit header {
      align-items: start;
      display: flex;
      gap: 1rem;
      justify-content: space-between;
    }

    .student-curriculum__header > p,
    .student-curriculum__unit-progress,
    .student-curriculum__lesson-objective,
    .student-curriculum__lesson-meta,
    .student-curriculum__state small,
    .student-curriculum__empty p {
      color: var(--ee-text-soft);
      line-height: 1.55;
    }

    .student-curriculum__eyebrow {
      color: var(--ee-text-muted);
      font-size: 0.76rem;
      font-weight: 900;
      letter-spacing: 0.12em;
      margin: 0 0 0.3rem;
      text-transform: uppercase;
    }

    h2,
    h3,
    p {
      letter-spacing: 0;
      margin: 0;
    }

    h2 {
      font-size: clamp(1.35rem, 3vw, 1.8rem);
    }

    h3 {
      font-size: 1.1rem;
    }

    .student-curriculum__units,
    .student-curriculum__lessons {
      display: grid;
      gap: 0.85rem;
      list-style: none;
      margin: 0;
      padding: 0;
    }

    .student-curriculum__unit {
      background: var(--ee-surface-muted, #f8fafc);
      border: 1px solid var(--ee-border);
      border-radius: var(--ee-radius, 6px);
      display: grid;
      gap: 0.75rem;
      padding: 1rem;
    }

    .student-curriculum__unit-progress {
      background: var(--ee-surface);
      border: 1px solid var(--ee-border);
      border-radius: 999px;
      display: inline-flex;
      font-size: 0.8rem;
      font-weight: 800;
      padding: 0.35rem 0.65rem;
      white-space: nowrap;
    }

    .student-curriculum__lesson {
      align-items: start;
      background: var(--ee-surface);
      border: 1px solid var(--ee-border);
      border-radius: var(--ee-radius, 6px);
      color: var(--ee-text);
      cursor: pointer;
      display: grid;
      gap: 0.85rem;
      grid-template-columns: auto minmax(0, 1fr) minmax(9rem, 0.28fr);
      min-height: 4.25rem;
      padding: 0.85rem;
      text-align: left;
      width: 100%;
    }

    .student-curriculum__lesson:focus-visible {
      outline: 3px solid var(--ee-focus-ring);
      outline-offset: 3px;
    }

    .student-curriculum__lesson:disabled {
      cursor: not-allowed;
      opacity: 0.82;
    }

    .student-curriculum__lesson--current {
      border-color: color-mix(in srgb, var(--ee-action-primary) 45%, var(--ee-border));
      box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--ee-action-primary) 18%, transparent);
    }

    .student-curriculum__lesson--complete {
      border-color: var(--ee-status-success-border, #22c55e);
    }

    .student-curriculum__lesson--locked {
      background: color-mix(in srgb, var(--ee-surface-muted, #f8fafc) 85%, var(--ee-surface));
    }

    .student-curriculum__lesson-index {
      align-items: center;
      background: var(--ee-surface-muted, #f8fafc);
      border: 1px solid var(--ee-border);
      border-radius: 999px;
      display: inline-flex;
      font-weight: 900;
      height: 2rem;
      justify-content: center;
      width: 2rem;
    }

    .student-curriculum__lesson-main {
      display: grid;
      gap: 0.3rem;
      min-width: 0;
    }

    .student-curriculum__lesson-title {
      font-weight: 900;
      overflow-wrap: anywhere;
    }

    .student-curriculum__lesson-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 0.55rem;
      font-size: 0.8rem;
      font-weight: 700;
    }

    .student-curriculum__state {
      align-items: start;
      display: grid;
      gap: 0.25rem;
      justify-items: end;
      text-align: right;
    }

    .student-curriculum__state > span {
      border: 1px solid var(--ee-border);
      border-radius: 999px;
      display: inline-flex;
      font-size: 0.75rem;
      font-weight: 900;
      padding: 0.35rem 0.65rem;
      white-space: nowrap;
    }

    .student-curriculum__state[data-state="current"] > span {
      background: var(--ee-color-action-primary-background, #0f766e);
      border-color: var(--ee-color-action-primary-border, #0f766e);
      color: var(--ee-color-action-primary-text, #fff);
    }

    .student-curriculum__state[data-state="complete"] > span {
      background: var(--ee-status-success-bg, #dcfce7);
      border-color: var(--ee-status-success-border, #22c55e);
      color: var(--ee-status-success-text, #166534);
    }

    .student-curriculum__state[data-state="locked"] > span,
    .student-curriculum__state[data-state="unavailable"] > span {
      background: var(--ee-surface-muted, #f8fafc);
      color: var(--ee-text-soft);
    }

    .student-curriculum__empty {
      border: 1px dashed var(--ee-border);
      border-radius: var(--ee-radius, 6px);
      display: grid;
      gap: 0.35rem;
      padding: 1rem;
    }

    @media (max-width: 720px) {
      .student-curriculum__header,
      .student-curriculum__unit header {
        display: grid;
      }

      .student-curriculum__lesson {
        grid-template-columns: auto minmax(0, 1fr);
      }

      .student-curriculum__state {
        grid-column: 1 / -1;
        justify-items: start;
        padding-inline-start: 2.85rem;
        text-align: left;
      }
    }
  `],
})
export class StudentCurriculumComponent {
  @Input() units: StudentCurriculumUnit[] = [];
  @Input() summaryLabel = 'Course curriculum';
  @Output() openLesson = new EventEmitter<StudentCurriculumLesson>();
}
