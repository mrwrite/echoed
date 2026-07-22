import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

let nextSelectId = 0;

@Component({
  selector: 'app-echo-select',
  standalone: true,
  template: `
    <div class="ee-field" [class.ee-field--invalid]="!!error" [class.ee-field--valid]="success && !error">
      <label class="ee-field__label" [for]="controlId">{{ label }} <span *ngIf="required" aria-hidden="true">*</span></label>
      <select class="ee-control" [id]="controlId" [name]="name" [disabled]="disabled || loading" [required]="required"
        [attr.aria-describedby]="describedBy" [attr.aria-invalid]="error ? 'true' : null" [attr.aria-busy]="loading || null"
        [ngModel]="value" (ngModelChange)="valueChange.emit($event)">
        <option *ngFor="let opt of options" [ngValue]="getValue(opt)">{{ getLabel(opt) }}</option>
      </select>
      <p *ngIf="hint && !error" class="ee-field__hint" [id]="hintId">{{ hint }}</p>
      <p *ngIf="error" class="ee-field__error" [id]="errorId" role="alert">{{ error }}</p>
      <p *ngIf="success && !error" class="ee-field__success" [id]="successId" role="status">{{ success }}</p>
    </div>
  `,
  imports: [CommonModule, FormsModule],
})
export class EchoSelectComponent {
  private readonly generatedId = `echo-select-${++nextSelectId}`;
  @Input() id = '';
  @Input() name = '';
  @Input() label = 'Select an option';
  @Input() options: (string | { label: string; value: any })[] = [];
  @Input() value: any;
  @Input() disabled = false;
  @Input() required = false;
  @Input() loading = false;
  @Input() hint = '';
  @Input() error = '';
  @Input() success = '';

  @Output() valueChange = new EventEmitter<any>();

  get controlId(): string { return this.id || this.generatedId; }
  get hintId(): string { return `${this.controlId}-hint`; }
  get errorId(): string { return `${this.controlId}-error`; }
  get successId(): string { return `${this.controlId}-success`; }
  get describedBy(): string | null {
    const ids = [this.hint && !this.error ? this.hintId : '', this.error ? this.errorId : '', this.success && !this.error ? this.successId : ''].filter(Boolean);
    return ids.length ? ids.join(' ') : null;
  }

  getLabel(option: any): string {
    return typeof option === 'string' ? option : option.label;
  }

  getValue(option: any): any {
    return typeof option === 'string' ? option : option.value;
  }
}
