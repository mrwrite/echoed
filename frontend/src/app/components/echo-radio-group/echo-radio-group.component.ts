import { Component, Input, Output, EventEmitter } from '@angular/core';
import { EchoRadioComponent } from '../echo-radio/echo-radio.component';
import { NgFor } from '@angular/common';

@Component({
  selector: 'app-echo-radio-group',
  standalone: true,
  imports: [EchoRadioComponent, NgFor],
  template: `
    <div class="flex flex-col gap-2">
      <app-echo-radio
        *ngFor="let option of options"
        [label]="option.label"
        [value]="option.value"
        [checked]="option.value === selectedValue"
        [name]="name"
        (valueChange)="onValueChange($event)"
      ></app-echo-radio>
    </div>
  `,
})
export class EchoRadioGroupComponent {
  @Input() options: { label: string; value: string }[] = [];
  @Input() selectedValue: string = '';
  @Input() name: string = 'radio-group';
  @Output() selectedValueChange = new EventEmitter<string>();

  onValueChange(value: string) {
    this.selectedValue = value;
    this.selectedValueChange.emit(value);
  }
}
