import { Component, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-echo-radio',
  standalone: true,
  template: `
    <label class="inline-flex items-center cursor-pointer">
      <input
        type="radio"
        class="form-radio w-5 h-5 text-primary border-gray-300 focus:ring-primary"
        [value]="value"
        [checked]="checked"
        (change)="onSelectionChange()"
        name="{{ name }}"
      />
      <span class="ml-2 text-sm font-medium">{{ label }}</span>
    </label>
  `,
})
export class EchoRadioComponent {
  @Input() label: string = 'Option';
  @Input() value!: string;
  @Input() checked: boolean = false;
  @Input() name: string = 'radio-group';
  @Output() valueChange = new EventEmitter<string>();

  onSelectionChange() {
    this.valueChange.emit(this.value);
  }
}
