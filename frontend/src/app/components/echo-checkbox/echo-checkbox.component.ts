import { CommonModule } from '@angular/common';
import { Component, Input, Output, EventEmitter } from '@angular/core';

let nextCheckboxId = 0;

@Component({
  selector: 'app-echo-checkbox',
  standalone: true,
  template: `
    <div class="ee-choice" [class.ee-field--invalid]="!!error">
    <label class="ee-choice__label">
      <input
        type="checkbox"
        class="ee-choice__control"
        [checked]="checked"
        [disabled]="disabled"
        [required]="required"
        [attr.aria-describedby]="error ? errorId : (hint ? hintId : null)"
        [attr.aria-invalid]="error ? 'true' : null"
        (change)="onToggle($event)"
      />
      <span>{{ label }} <span *ngIf="required" aria-hidden="true">*</span></span>
    </label>
    <p *ngIf="hint && !error" class="ee-field__hint" [id]="hintId">{{ hint }}</p>
    <p *ngIf="error" class="ee-field__error" [id]="errorId" role="alert">{{ error }}</p>
    </div>
  `,
  imports: [CommonModule],
})
export class EchoCheckboxComponent {
  @Input() label: string = 'Checkbox';
  @Input() checked: boolean = false;
  @Input() disabled = false;
  @Input() required = false;
  @Input() hint = '';
  @Input() error = '';
  @Output() checkedChange = new EventEmitter<boolean>();

  readonly hintId = `echo-checkbox-${++nextCheckboxId}-hint`;
  readonly errorId = `${this.hintId}-error`;

  onToggle(event: Event) {
    const input = event.target as HTMLInputElement;
    this.checkedChange.emit(input.checked);
  }
}
