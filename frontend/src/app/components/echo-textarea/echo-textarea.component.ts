import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

let nextTextareaId = 0;

@Component({
  selector: 'app-echo-textarea',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="ee-field" [class.ee-field--invalid]="!!error" [class.ee-field--valid]="success && !error">
      <label class="ee-field__label" [for]="controlId">{{ label }} <span *ngIf="required" aria-hidden="true">*</span></label>
      <textarea class="ee-control ee-control--textarea" [id]="controlId" [name]="name" [placeholder]="placeholder" [rows]="rows"
        [disabled]="disabled || loading" [required]="required" [attr.aria-describedby]="describedBy"
        [attr.aria-invalid]="error ? 'true' : null" [attr.aria-busy]="loading || null"
        [ngModel]="value" (ngModelChange)="valueChange.emit($event)"></textarea>
      <p *ngIf="hint && !error" class="ee-field__hint" [id]="hintId">{{ hint }}</p>
      <p *ngIf="error" class="ee-field__error" [id]="errorId" role="alert">{{ error }}</p>
      <p *ngIf="success && !error" class="ee-field__success" [id]="successId" role="status">{{ success }}</p>
    </div>
  `,
})
export class EchoTextareaComponent {
  private readonly generatedId = `echo-textarea-${++nextTextareaId}`;
  @Input() id = '';
  @Input() name = '';
  @Input() label = 'Message';
  @Input() placeholder: string = '';
  @Input() value: string = '';
  @Input() rows: number = 4;
  @Input() disabled = false;
  @Input() required = false;
  @Input() loading = false;
  @Input() hint = '';
  @Input() error = '';
  @Input() success = '';

  @Output() valueChange = new EventEmitter<string>();

  get controlId(): string { return this.id || this.generatedId; }
  get hintId(): string { return `${this.controlId}-hint`; }
  get errorId(): string { return `${this.controlId}-error`; }
  get successId(): string { return `${this.controlId}-success`; }
  get describedBy(): string | null {
    const ids = [this.hint && !this.error ? this.hintId : '', this.error ? this.errorId : '', this.success && !this.error ? this.successId : ''].filter(Boolean);
    return ids.length ? ids.join(' ') : null;
  }
}
