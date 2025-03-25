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
        'rounded-lg px-4 py-2 font-bold tracking-wide text-white transition',
        color === 'primary' ? 'bg-primary hover:bg-primary/90' :
        color === 'accent' ? 'bg-accent hover:bg-accent/90 text-black' :
        color === 'warn' ? 'bg-warn hover:bg-warn/90' : '',
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
  @Input() color: 'primary' | 'accent' | 'warn' = 'primary';
  @Input() disabled = false;
}
