import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

import { IconModule } from '../../shared/icon/icon.module';

export type EchoLoadingDensity = 'page' | 'section' | 'compact';

@Component({
  selector: 'app-echo-loading-state',
  standalone: true,
  imports: [CommonModule, IconModule],
  templateUrl: './echo-loading-state.component.html',
  styleUrl: './echo-loading-state.component.scss',
})
export class EchoLoadingStateComponent {
  @Input() title = 'Loading';
  @Input() body = 'Please wait while the latest state is prepared.';
  @Input() density: EchoLoadingDensity = 'section';
  @Input() ariaLabel = 'loading-state';
  @Input() centered = false;
}
