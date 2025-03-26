import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-echo-select',
  standalone: true,
  template: `
    <label *ngIf="label" class="block mb-1 font-semibold text-sm text-gray-700">{{ label }}</label>
    <select
      class="w-full px-4 py-2 rounded-lg border border-gray-300 bg-white focus:outline-none focus:ring-2 focus:ring-primary transition"
      [disabled]="disabled"
      [ngModel]="value"
      (ngModelChange)="valueChange.emit($event)"
    >
      <option *ngFor="let opt of options" [value]="getValue(opt)">
        {{ getLabel(opt) }}
      </option>
    </select>
  `,
  imports: [CommonModule, FormsModule],
})
export class EchoSelectComponent {
  @Input() label?: string;
  @Input() options: (string | { label: string; value: any })[] = [];
  @Input() value: any;
  @Input() disabled = false;

  @Output() valueChange = new EventEmitter<any>();

  getLabel(option: any): string {
    return typeof option === 'string' ? option : option.label;
  }

  getValue(option: any): any {
    return typeof option === 'string' ? option : option.value;
  }
}
