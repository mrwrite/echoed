import { Component, Input, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-echo-tooltip',
  standalone: true,
  imports: [CommonModule],
  template: `
    <span class="relative inline-block" (mouseenter)="show()" (mouseleave)="hide()">
      <ng-content></ng-content>
      <span *ngIf="visible"
            [ngClass]="[
              'absolute z-50 px-2 py-1 text-xs rounded shadow-md transition-opacity duration-300',
              positionClasses,
              'bg-gray-800 text-white'
            ]"
            [style.opacity]="visible ? 1 : 0">
        {{ text }}
      </span>
    </span>
  `,
})
export class EchoTooltipComponent {
  @Input() text: string = '';
  @Input() position: 'top' | 'bottom' | 'left' | 'right' = 'top';
  visible = false;

  show() { this.visible = true; }
  hide() { this.visible = false; }

  get positionClasses() {
    switch (this.position) {
      case 'top': return 'bottom-full left-1/2 transform -translate-x-1/2 mb-2';
      case 'bottom': return 'top-full left-1/2 transform -translate-x-1/2 mt-2';
      case 'left': return 'right-full top-1/2 transform -translate-y-1/2 mr-2';
      case 'right': return 'left-full top-1/2 transform -translate-y-1/2 ml-2';
      default: return '';
    }
  }
}
