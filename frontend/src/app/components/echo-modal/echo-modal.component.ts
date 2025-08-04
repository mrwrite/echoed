import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-echo-modal',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      *ngIf="open"
      (click)="handleBackdropClick()"
    >
      <div
        class="bg-white dark:bg-gray-900 rounded-lg shadow-lg max-w-md w-full p-6"
        (click)="$event.stopPropagation()"
      >
        <div class="text-xl font-bold mb-4">{{ title }}</div>
        <div class="text-sm text-gray-600 dark:text-gray-300 mb-6">
          {{ description }}
        </div>
        <div class="flex justify-end space-x-2">
          <button
            *ngIf="showCancel"
            class="bg-warn text-white px-4 py-2 rounded hover:bg-warn/90"
            (click)="cancel.emit()"
          >
            {{ cancelText }}
          </button>
          <button
            class="bg-primary text-white px-4 py-2 rounded hover:bg-primary/90"
            (click)="confirm.emit()"
          >
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  `,
})
export class EchoModalComponent {
  @Input() open = false;
  @Input() title = 'Are you sure?';
  @Input() description = 'This action cannot be undone.';
  @Input() confirmText = 'Confirm';
  @Input() cancelText = 'Cancel';
  @Input() showCancel = true;
  @Output() cancel = new EventEmitter<void>();
  @Output() confirm = new EventEmitter<void>();

  handleBackdropClick() {
    this.cancel.emit();
  }
}
