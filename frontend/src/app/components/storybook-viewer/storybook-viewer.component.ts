import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
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
      <div class="space-y-2" *ngIf="orderedPages.length">
        <img [src]="orderedPages[currentIndex].image_url" class="w-full rounded max-h-[60vh] object-contain" alt="Storybook page" />
        <div class="flex" [ngClass]="currentIndex > 0 ? 'justify-between' : 'justify-end'">
          <button *ngIf="currentIndex > 0" class="px-2 py-1 bg-gray-200 rounded" (click)="prev()">Prev</button>
          <button *ngIf="currentIndex < orderedPages.length - 1" class="px-2 py-1 bg-gray-200 rounded" (click)="next()">Next</button>
        </div>
      </div>
  `
})
export class StorybookViewerComponent implements OnChanges {
  @Input() pages: StorybookPage[] = [];
  currentIndex = 0;

  get orderedPages(): StorybookPage[] {
    return [...(this.pages || [])].sort((left, right) => {
      const leftOrder = left.order ?? Number.MAX_SAFE_INTEGER;
      const rightOrder = right.order ?? Number.MAX_SAFE_INTEGER;
      if (leftOrder !== rightOrder) {
        return leftOrder - rightOrder;
      }
      return 0;
    });
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['pages']) {
      this.currentIndex = 0;
    }
  }

  prev() {
    if (this.currentIndex > 0) this.currentIndex--;
  }

  next() {
    if (this.currentIndex < this.orderedPages.length - 1) this.currentIndex++;
  }
}
