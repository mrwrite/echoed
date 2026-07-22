import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

let nextSearchId = 0;

@Component({
  selector: 'app-echo-search',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="ee-field ee-search">
      <label class="ee-field__label" [for]="controlId">{{ label }}</label>
      <div class="ee-search__control">
        <span class="ee-search__icon" aria-hidden="true">⌕</span>
        <input class="ee-control" type="search" [id]="controlId" [name]="name" [value]="value"
          [placeholder]="placeholder" [disabled]="disabled || loading" [attr.aria-describedby]="describedBy"
          [attr.aria-busy]="loading || null" (input)="onInput($event)" />
        <button *ngIf="value" type="button" class="ee-search__clear" [disabled]="disabled || loading"
          [attr.aria-label]="clearLabel" (click)="clear()">Clear</button>
      </div>
      <p *ngIf="hint" class="ee-field__hint" [id]="hintId">{{ hint }}</p>
      <p *ngIf="resultCount !== null" class="ee-field__status" [id]="statusId" role="status" aria-live="polite">
        {{ resultCount }} {{ resultCount === 1 ? resultLabel : resultLabelPlural }}
      </p>
    </div>
  `,
})
export class EchoSearchComponent {
  private readonly generatedId = `echo-search-${++nextSearchId}`;
  @Input() id = '';
  @Input() name = 'search';
  @Input() label = 'Search';
  @Input() placeholder = '';
  @Input() value = '';
  @Input() disabled = false;
  @Input() loading = false;
  @Input() hint = '';
  @Input() resultCount: number | null = null;
  @Input() resultLabel = 'result';
  @Input() resultLabelPlural = 'results';
  @Input() clearLabel = 'Clear search';
  @Output() valueChange = new EventEmitter<string>();
  @Output() cleared = new EventEmitter<void>();

  get controlId(): string { return this.id || this.generatedId; }
  get hintId(): string { return `${this.controlId}-hint`; }
  get statusId(): string { return `${this.controlId}-status`; }
  get describedBy(): string | null {
    const ids = [this.hint ? this.hintId : '', this.resultCount !== null ? this.statusId : ''].filter(Boolean);
    return ids.length ? ids.join(' ') : null;
  }

  onInput(event: Event): void {
    this.value = (event.target as HTMLInputElement).value;
    this.valueChange.emit(this.value);
  }

  clear(): void {
    this.value = '';
    this.valueChange.emit('');
    this.cleared.emit();
  }
}
