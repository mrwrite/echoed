import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-echo-textarea',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <label *ngIf="label" class="block mb-1 font-semibold text-sm text-gray-700">{{ label }}</label>
    <textarea
      class="w-full px-4 py-2 rounded-lg border border-gray-300 bg-white focus:outline-none focus:ring-2 focus:ring-primary transition resize-none"
      [placeholder]="placeholder"
      [rows]="rows"
      [disabled]="disabled"
      [ngModel]="value"
      (ngModelChange)="valueChange.emit($event)"
    ></textarea>
  `,
})
export class EchoTextareaComponent {
  @Input() label?: string;
  @Input() placeholder: string = '';
  @Input() value: string = '';
  @Input() rows: number = 4;
  @Input() disabled = false;

  @Output() valueChange = new EventEmitter<string>();
}