// echo-button.component.ts
import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  standalone: true,
  selector: 'app-echo-button',
  imports: [CommonModule],
  template: `
    <button
      [type]="type"
      [ngClass]="[
        'ee-button',
        'ee-button--' + size,
        color === 'secondary' ? 'ee-button--secondary' : '',
        color === 'tertiary' ? 'ee-button--secondary' : '',
        color === 'warn' ? 'ee-button--warn' : '',
        iconOnly ? 'ee-button--icon' : '',
        loading ? 'ee-button--loading' : '',
        disabled || loading ? 'opacity-50 cursor-not-allowed' : ''
      ]"
      [disabled]="disabled || loading"
      [attr.aria-label]="ariaLabel || (iconOnly ? label : null)"
      [attr.aria-busy]="loading || null"
      [attr.title]="iconOnly ? (tooltip || ariaLabel || label) : null"
    >
      <span *ngIf="loading" class="ee-button__spinner" aria-hidden="true"></span>
      <span *ngIf="icon" class="ee-button__icon" aria-hidden="true">{{ icon }}</span>
      <span *ngIf="!iconOnly">{{ loading ? loadingLabel : label }}</span>
    </button>
  `,
})
export class EchoButtonComponent {
  @Input() label: string = 'Echo Button';
  @Input() color: 'primary' | 'accent' | 'secondary' | 'warn' | 'tertiary' = 'primary';
  @Input() disabled = false;
  @Input() ariaLabel = '';
  @Input() type: 'button' | 'submit' | 'reset' = 'button';
  @Input() size: 'sm' | 'md' | 'lg' = 'md';
  @Input() loading = false;
  @Input() loadingLabel = 'Working';
  @Input() icon = '';
  @Input() iconOnly = false;
  @Input() tooltip = '';
}
