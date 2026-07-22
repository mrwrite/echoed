import { Component, Input, Output, EventEmitter } from '@angular/core';
import { NgClass, NgIf } from '@angular/common';

let nextToggleId = 0;

@Component({
  selector: 'app-echo-toggle',
  standalone: true,
  imports: [NgClass, NgIf],
  template: `
    <div class="ee-choice">
      <button type="button" class="ee-switch" role="switch" [class.ee-switch--checked]="checked"
        [attr.aria-checked]="checked" [attr.aria-describedby]="hint ? hintId : null" [disabled]="disabled" (click)="toggle()">
        <span class="ee-switch__track" aria-hidden="true"><span class="ee-switch__thumb"></span></span>
        <span>{{ label }}</span>
      </button>
      <p *ngIf="hint" class="ee-field__hint" [id]="hintId">{{ hint }}</p>
    </div>
  `,
})
export class EchoToggleComponent {
  @Input() checked = false;
  @Input() label = '';
  @Input() disabled = false;
  @Input() hint = '';
  @Output() checkedChange = new EventEmitter<boolean>();
  readonly hintId = `echo-toggle-${++nextToggleId}-hint`;

  toggle() {
    if (this.disabled) return;
    this.checked = !this.checked;
    this.checkedChange.emit(this.checked);
  }
}
