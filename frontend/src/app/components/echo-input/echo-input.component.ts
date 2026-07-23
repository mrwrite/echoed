import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

let nextInputId = 0;

@Component({
  selector: 'app-echo-input',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="ee-field" [class.ee-field--invalid]="!!error" [class.ee-field--valid]="success && !error">
      <label class="ee-field__label" [for]="controlId">
        {{ label }} <span *ngIf="required" aria-hidden="true">*</span>
      </label>
      <input
        class="ee-control"
        [id]="controlId"
        [name]="name"
        [type]="type"
        [placeholder]="placeholder"
        [value]="value"
        [disabled]="disabled || loading"
        [required]="required"
        [attr.autocomplete]="autocomplete || null"
        [attr.aria-describedby]="describedBy"
        [attr.aria-invalid]="error ? 'true' : null"
        [attr.aria-busy]="loading || null"
        (input)="onInput($event)"
      />
      <p *ngIf="hint && !error" class="ee-field__hint" [id]="hintId">{{ hint }}</p>
      <p *ngIf="error" class="ee-field__error" [id]="errorId" role="alert">{{ error }}</p>
      <p *ngIf="success && !error" class="ee-field__success" [id]="successId" role="status">{{ success }}</p>
    </div>
  `,
})
export class EchoInputComponent {
  private readonly generatedId = `echo-input-${++nextInputId}`;
  @Input() id = '';
  @Input() name = '';
  @Input() label = 'Text input';
  @Input() type: string = 'text';
  @Input() placeholder = '';
  @Input() value: string = '';
  @Input() disabled = false;
  @Input() required = false;
  @Input() loading = false;
  @Input() hint = '';
  @Input() error = '';
  @Input() success = '';
  @Input() autocomplete = '';
  @Output() valueChange = new EventEmitter<string>();

  get controlId(): string { return this.id || this.generatedId; }
  get hintId(): string { return `${this.controlId}-hint`; }
  get errorId(): string { return `${this.controlId}-error`; }
  get successId(): string { return `${this.controlId}-success`; }
  get describedBy(): string | null {
    const ids = [this.hint && !this.error ? this.hintId : '', this.error ? this.errorId : '', this.success && !this.error ? this.successId : ''].filter(Boolean);
    return ids.length ? ids.join(' ') : null;
  }

  onInput(event: Event) {
    const input = event.target as HTMLInputElement;
    this.valueChange.emit(input.value);
  }
}
