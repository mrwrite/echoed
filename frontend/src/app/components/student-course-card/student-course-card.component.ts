import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IconModule } from '../../shared/icon/icon.module';

@Component({
  selector: 'app-student-course-card',
  standalone: true,
  imports: [CommonModule, IconModule],
  template: `
    <div class="bg-white rounded-xl shadow w-full overflow-hidden relative">
      <img *ngIf="thumbnailUrl" [src]="thumbnailUrl" alt="Course image" class="w-full h-48 object-cover">
      <div class="p-6">
        <p class="text-xl font-bold text-primary">{{ title }}</p>
        <p *ngIf="instructor" class="text-xs text-gray-500 mb-1">By {{ instructor }}</p>
        <p class="text-xs text-gray-500">{{ description }}</p>
        <div *ngIf="rating" class="flex items-center text-sm text-yellow-500 mt-1">
          <ng-container *ngFor="let star of [1,2,3,4,5]">
            <lucide-icon [name]="star <= (rating || 0) ? 'star' : 'star'" class="h-4 w-4" [class.opacity-30]="star > (rating || 0)"></lucide-icon>
          </ng-container>
          <span *ngIf="ratingCount" class="text-gray-500 ml-1">({{ ratingCount }})</span>
        </div>
        <div *ngIf="progress !== undefined" class="mt-2">
          <div class="flex items-center gap-2">
            <div class="h-2 bg-gray-200 rounded-full overflow-hidden flex-1">
              <div class="h-full bg-primary" [style.width.%]="progress"></div>
            </div>
            <span class="text-xs font-medium">{{ progress }}%</span>
          </div>
        </div>
        <ng-content></ng-content>
      </div>
      <span
        *ngIf="status === 'completed'"
        class="absolute top-4 right-4 bg-green-600 text-white text-xs px-3 py-1 rounded"
      >Completed</span>
    </div>
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
