// echo-button.component.ts
import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  standalone: true,
  selector: 'app-echo-button',
  imports: [CommonModule],
  template: `
    <button
      [ngClass]="[
        'ee-button',
        color === 'tertiary' ? 'ee-button--secondary' : '',
        color === 'warn' ? 'ee-button--warn' : '',
        disabled ? 'opacity-50 cursor-not-allowed' : ''
      ]"
      [disabled]="disabled"
    >
      {{ label }}
    </button>
  `,
})
export class EchoButtonComponent {
  @Input() label: string = 'Echo Button';
  @Input() color: 'primary' | 'accent' | 'warn' | 'tertiary' = 'primary';
  @Input() disabled = false;
}
