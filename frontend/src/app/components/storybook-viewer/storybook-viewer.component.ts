import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface StorybookPage {
  image_url: string;
  order?: number;
}

@Component({
  selector: 'app-storybook-viewer',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="space-y-2" *ngIf="pages && pages.length">
      <img [src]="pages[currentIndex].image_url" class="w-full rounded max-h-[60vh] object-contain" />
      <div class="flex justify-between">
        <button *ngIf="currentIndex > 0" class="px-2 py-1 bg-gray-200 rounded" (click)="prev()">Prev</button>
        <button *ngIf="currentIndex < pages.length - 1" class="px-2 py-1 bg-gray-200 rounded" (click)="next()">Next</button>
      </div>
    </div>
  `
})
export class StorybookViewerComponent {
  @Input() pages: StorybookPage[] = [];
  currentIndex = 0;

  prev() {
    if (this.currentIndex > 0) this.currentIndex--;
  }

  next() {
    if (this.currentIndex < this.pages.length - 1) this.currentIndex++;
  }
}
