import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

@Component({
  standalone: true,
  selector: 'app-ee-card',
  imports: [CommonModule],
  template: `<article class="ee-card" [class.ee-card--interactive]="interactive"><ng-content></ng-content></article>`,
})
export class EECardComponent {
  @Input() interactive = false;
}

@Component({
  standalone: true,
  selector: 'app-ee-hero',
  imports: [CommonModule],
  template: `
    <header class="ee-hero">
      <p class="ee-eyebrow" *ngIf="eyebrow">{{ eyebrow }}</p>
      <h1 class="ee-page-title">{{ title }}</h1>
      <p class="ee-page-copy" *ngIf="copy">{{ copy }}</p>
      <ng-content></ng-content>
    </header>
  `,
})
export class EEHeroComponent {
  @Input() eyebrow = '';
  @Input() title = '';
  @Input() copy = '';
}

@Component({
  standalone: true,
  selector: 'app-ee-section',
  imports: [CommonModule],
  template: `
    <section class="ee-section">
      <div class="ee-panel-header" *ngIf="eyebrow || title || description">
        <div>
          <p class="ee-eyebrow" *ngIf="eyebrow">{{ eyebrow }}</p>
          <h2 *ngIf="title">{{ title }}</h2>
          <p class="ee-muted" *ngIf="description">{{ description }}</p>
        </div>
        <ng-content select="[actions]"></ng-content>
      </div>
      <ng-content></ng-content>
    </section>
  `,
})
export class EESectionComponent {
  @Input() eyebrow = '';
  @Input() title = '';
  @Input() description = '';
}

@Component({
  standalone: true,
  selector: 'app-ee-button',
  imports: [CommonModule],
  template: `
    <button class="ee-button" [class.ee-button--secondary]="variant === 'secondary'" [disabled]="disabled" [type]="type">
      <ng-content>{{ label }}</ng-content>
    </button>
  `,
})
export class EEButtonComponent {
  @Input() label = '';
  @Input() variant: 'primary' | 'secondary' = 'primary';
  @Input() disabled = false;
  @Input() type: 'button' | 'submit' | 'reset' = 'button';
}

@Component({
  standalone: true,
  selector: 'app-ee-badge',
  imports: [CommonModule],
  template: `<span class="ee-badge" [ngClass]="statusClass"><ng-content>{{ label }}</ng-content></span>`,
})
export class EEBadgeComponent {
  @Input() label = '';
  @Input() status = '';

  get statusClass(): string {
    return this.status ? `ee-badge--${this.status.replace(/_/g, '-')}` : '';
  }
}

@Component({
  standalone: true,
  selector: 'app-ee-metric',
  imports: [CommonModule],
  template: `<article class="ee-metric"><span>{{ label }}</span><strong>{{ value }}</strong><ng-content></ng-content></article>`,
})
export class EEMetricComponent {
  @Input() label = '';
  @Input() value: string | number = '';
}

@Component({
  standalone: true,
  selector: 'app-ee-input',
  imports: [CommonModule],
  template: `
    <label class="ee-input">
      <span>{{ label }}</span>
      <input [attr.name]="name" [attr.type]="type" [attr.placeholder]="placeholder" [disabled]="disabled" />
    </label>
  `,
})
export class EEInputComponent {
  @Input() label = '';
  @Input() name = '';
  @Input() type = 'text';
  @Input() placeholder = '';
  @Input() disabled = false;
}

@Component({
  standalone: true,
  selector: 'app-ee-form-section',
  imports: [CommonModule],
  template: `<section class="ee-form-section"><ng-content></ng-content></section>`,
})
export class EEFormSectionComponent {}

@Component({
  standalone: true,
  selector: 'app-ee-stat-card',
  imports: [CommonModule],
  template: `<article class="ee-stat-card"><span>{{ label }}</span><strong>{{ value }}</strong><p *ngIf="detail">{{ detail }}</p></article>`,
})
export class EEStatCardComponent {
  @Input() label = '';
  @Input() value: string | number = '';
  @Input() detail = '';
}

@Component({
  standalone: true,
  selector: 'app-ee-timeline',
  imports: [CommonModule],
  template: `<ol class="ee-timeline"><ng-content></ng-content></ol>`,
})
export class EETimelineComponent {}

@Component({
  standalone: true,
  selector: 'app-ee-empty-state',
  imports: [CommonModule],
  template: `<div class="ee-empty-state"><strong>{{ title }}</strong><span>{{ description }}</span><ng-content></ng-content></div>`,
})
export class EEEmptyStateComponent {
  @Input() title = '';
  @Input() description = '';
}

@Component({
  standalone: true,
  selector: 'app-ee-stepper',
  imports: [CommonModule],
  template: `<ol class="ee-stepper"><ng-content></ng-content></ol>`,
})
export class EEStepperComponent {}

@Component({
  standalone: true,
  selector: 'app-ee-tag',
  imports: [CommonModule],
  template: `<span class="ee-tag"><ng-content>{{ label }}</ng-content></span>`,
})
export class EETagComponent {
  @Input() label = '';
}

@Component({
  standalone: true,
  selector: 'app-ee-navigation-card',
  imports: [CommonModule],
  template: `<article class="ee-navigation-card"><ng-content></ng-content></article>`,
})
export class EENavigationCardComponent {}
