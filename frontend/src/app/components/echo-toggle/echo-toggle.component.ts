import { Component, Input, Output, EventEmitter } from '@angular/core';
import { NgClass } from '@angular/common';

@Component({
  selector: 'app-echo-toggle',
  standalone: true,
  imports: [NgClass],
  template: `
    <label class="flex items-center gap-2 cursor-pointer select-none">
      <div
        class="relative w-12 h-6 rounded-full transition-colors duration-200"
        [ngClass]="checked ? 'bg-primary' : 'bg-gray-300'"
      >
        <div
          class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform duration-200"
          [ngClass]="{ 'translate-x-6': checked }"
        ></div>
      </div>
      <input
        type="checkbox"
        class="hidden"
        [checked]="checked"
        (change)="toggle()"
      />
      <span *ngIf="label">{{ label }}</span>
    </label>
  `,
})
export class EchoToggleComponent {
  @Input() checked = false;
  @Input() label = '';
  @Output() checkedChange = new EventEmitter<boolean>();

  toggle() {
    this.checked = !this.checked;
    this.checkedChange.emit(this.checked);
  }
}