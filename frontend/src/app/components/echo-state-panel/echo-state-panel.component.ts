import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

import { IconModule } from '../../shared/icon/icon.module';

export type EchoStateVariant =
  | 'empty'
  | 'error'
  | 'unavailable'
  | 'blocked'
  | 'permission'
  | 'success';

@Component({
  selector: 'app-echo-state-panel',
  standalone: true,
  imports: [CommonModule, IconModule],
  templateUrl: './echo-state-panel.component.html',
  styleUrl: './echo-state-panel.component.scss',
})
export class EchoStatePanelComponent {
  @Input() variant: EchoStateVariant = 'empty';
  @Input() title = 'State unavailable';
  @Input() body = '';
  @Input() context = '';
  @Input() impact = '';
  @Input() eyebrow = '';
  @Input() actionLabel?: string;
  @Input() actionAriaLabel?: string;
  @Input() secondaryActionLabel?: string;
  @Input() secondaryActionAriaLabel?: string;
  @Input() ariaLabel?: string;
  @Input() compact = false;
  @Input() iconName?: string;
  @Input() align: 'left' | 'center' = 'left';

  @Output() action = new EventEmitter<void>();
  @Output() secondaryAction = new EventEmitter<void>();

  get role(): 'status' | 'alert' {
    return this.variant === 'error' ? 'alert' : 'status';
  }

  get ariaLive(): 'polite' | 'assertive' {
    return this.variant === 'error' ? 'assertive' : 'polite';
  }

  get resolvedAriaLabel(): string {
    return this.ariaLabel || this.title;
  }

  get resolvedIconName(): string {
    if (this.iconName) {
      return this.iconName;
    }

    switch (this.variant) {
      case 'permission':
        return 'Lock';
      case 'success':
        return 'CheckCircle';
      case 'blocked':
        return 'Users';
      case 'unavailable':
        return 'BookOpen';
      case 'error':
        return 'Settings';
      case 'empty':
      default:
        return 'FileText';
    }
  }
}
