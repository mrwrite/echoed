import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-echo-badge',
  imports: [CommonModule],
  standalone: true,
  template: `
    <span
      [ngClass]="[
        'inline-block px-2 py-0.5 text-xs font-semibold rounded-full',
        variant === 'primary' ? 'bg-primary text-white' :
        variant === 'accent' ? 'bg-accent text-black' :
        variant === 'warn' ? 'bg-warn text-white' :
        'bg-gray-200 text-gray-800'
      ]"
    >
      {{ label }}
    </span>
  `,
})
export class EchoBadgeComponent {
  @Input() label: string = 'Badge';
  @Input() variant: 'primary' | 'accent' | 'warn' | 'neutral' = 'primary';
}
