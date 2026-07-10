import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-echo-skeleton',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div
      class="echo-skeleton"
      [class.echo-skeleton--text]="variant === 'text'"
      [class.echo-skeleton--circle]="variant === 'circle'"
      [class.echo-skeleton--block]="variant === 'block'"
      [style.width]="width"
      [style.height]="height"
      aria-hidden="true"
    ></div>
  `,
  styles: [`
    .echo-skeleton {
      animation: echo-skeleton-pulse var(--ee-motion-duration-slow, 260ms) var(--ee-motion-easing-standard, ease) infinite alternate;
      background: var(--ee-color-paper-200, #eadfce);
      border-radius: var(--ee-radius-card-default, 0.5rem);
      min-height: 1rem;
    }

    .echo-skeleton--text {
      border-radius: var(--ee-radius-control-pill, 999px);
      height: 1rem;
    }

    .echo-skeleton--circle {
      aspect-ratio: 1;
      border-radius: 999px;
    }

    .echo-skeleton--block {
      min-height: 6rem;
    }

    @keyframes echo-skeleton-pulse {
      from { opacity: 0.58; }
      to { opacity: 0.9; }
    }

    @media (prefers-reduced-motion: reduce) {
      .echo-skeleton {
        animation: none;
      }
    }
  `],
})
export class EchoSkeletonComponent {
  @Input() variant: 'text' | 'circle' | 'block' = 'block';
  @Input() width = '100%';
  @Input() height = '';
}
