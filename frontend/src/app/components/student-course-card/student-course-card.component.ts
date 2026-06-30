import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IconModule } from '../../shared/icon/icon.module';

@Component({
  selector: 'app-student-course-card',
  standalone: true,
  imports: [CommonModule, IconModule],
  template: `
    <article class="student-course-card relative w-full overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-soft-card">
      <img
        *ngIf="thumbnailUrl"
        [src]="thumbnailUrl"
        alt="Course image"
        class="h-48 w-full object-cover"
      />
      <div class="p-5 md:p-6">
        <div class="flex flex-wrap items-start justify-between gap-3">
          <p class="text-lg font-bold leading-7 text-primary md:text-xl">{{ title }}</p>
          <span
            class="rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em]"
            [ngClass]="
              status === 'completed'
                ? 'border border-emerald-200 bg-emerald-50 text-emerald-800'
                : (progress || 0) > 0 || status === 'active'
                ? 'border border-primary/15 bg-primary/5 text-primary'
                : 'border border-slate-200 bg-slate-50 text-slate-700'
            "
          >
            {{
              status === 'completed'
                ? 'Completed'
                : ((progress || 0) > 0 || status === 'active')
                ? 'In progress'
                : 'Ready to begin'
            }}
          </span>
        </div>
        <p *ngIf="instructor" class="mb-1 mt-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
          By {{ instructor }}
        </p>
        <p class="text-sm leading-6 text-slate-700">{{ description }}</p>
        <div
          *ngIf="rating"
          class="mt-3 flex items-center text-sm text-yellow-500"
        >
          <ng-container *ngFor="let star of [1, 2, 3, 4, 5]">
            <span
              aria-hidden="true"
              class="inline-block h-4 w-4 rounded-full bg-current"
              [class.opacity-30]="star > (rating || 0)"
            ></span>
          </ng-container>
          <span *ngIf="ratingCount" class="ml-1 text-slate-500"
            >({{ ratingCount }})</span
          >
        </div>
        <div *ngIf="progress !== undefined" class="mt-4">
          <div class="mb-2 flex items-center justify-between gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
            <span>Progress</span>
            <span>{{ progress }}%</span>
          </div>
          <div class="flex items-center gap-3">
            <div class="h-2.5 flex-1 overflow-hidden rounded-full bg-slate-200">
              <div class="h-full rounded-full bg-gradient-to-r from-primary to-accent" [style.width.%]="progress"></div>
            </div>
          </div>
        </div>
        <div class="mt-4">
          <ng-content></ng-content>
        </div>
      </div>
    </article>
  `,
})
export class StudentCourseCardComponent {
  @Input() title = '';
  @Input() description = '';
  @Input() thumbnailUrl?: string;
  @Input() instructor?: string;
  @Input() rating?: number;
  @Input() ratingCount?: number;
  /** Progress percentage from 0 to 100 */
  @Input() progress?: number;
  @Input() status?: string;
}
