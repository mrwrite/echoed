import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-student-course-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="bg-white p-6 rounded-xl shadow w-full">
      <p class="text-xl font-bold text-primary">{{ title }}</p>
      <p class="text-xs text-gray-500">{{ description }}</p>
      <div *ngIf="progress !== undefined" class="mt-2">
        <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div class="h-full bg-primary" [style.width.%]="progress"></div>
        </div>
      </div>
      <ng-content></ng-content>
    </div>
  `,
})
export class StudentCourseCardComponent {
  @Input() title = '';
  @Input() description = '';
  /** Progress percentage from 0 to 100 */
  @Input() progress?: number;
}
