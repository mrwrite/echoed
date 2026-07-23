import { Component, Input, Output, EventEmitter } from '@angular/core';
import { EchoRadioComponent } from '../echo-radio/echo-radio.component';
import { NgFor, NgIf } from '@angular/common';

let nextRadioGroupId = 0;

@Component({
  selector: 'app-echo-radio-group',
  standalone: true,
  imports: [EchoRadioComponent, NgFor, NgIf],
  template: `
    <fieldset class="ee-choice-group" [attr.aria-describedby]="error ? errorId : (hint ? hintId : null)">
      <legend>{{ label }} <span *ngIf="required" aria-hidden="true">*</span></legend>
      <app-echo-radio
        *ngFor="let option of options"
        [label]="option.label"
        [value]="option.value"
        [checked]="option.value === selectedValue"
        [name]="name"
        [disabled]="disabled"
        [describedBy]="error ? errorId : (hint ? hintId : '')"
        (valueChange)="onValueChange($event)"
      ></app-echo-radio>
      <p *ngIf="hint && !error" class="ee-field__hint" [id]="hintId">{{ hint }}</p>
      <p *ngIf="error" class="ee-field__error" [id]="errorId" role="alert">{{ error }}</p>
    </fieldset>
  `,
})
export class EchoRadioGroupComponent {
  @Input() options: { label: string; value: string }[] = [];
  @Input() selectedValue: string = '';
  @Input() name: string = 'radio-group';
  @Input() label = 'Choose an option';
  @Input() required = false;
  @Input() disabled = false;
  @Input() hint = '';
  @Input() error = '';
  @Output() selectedValueChange = new EventEmitter<string>();

  readonly hintId = `echo-radio-group-${++nextRadioGroupId}-hint`;
  readonly errorId = `${this.hintId}-error`;

  onValueChange(value: string) {
    this.selectedValue = value;
    this.selectedValueChange.emit(value);
  }
}
