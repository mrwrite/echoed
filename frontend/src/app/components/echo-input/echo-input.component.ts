import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-echo-input',
  standalone: true,
  template: `
    <input
      [type]="type"
      [placeholder]="placeholder"
      [value]="value"
      [disabled]="disabled"
      (input)="onInput($event)"
      class="w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary transition"
    />
  `,
})
export class EchoInputComponent {
  @Input() type: string = 'text';
  @Input() placeholder: string = 'Enter text';
  @Input() value: string = '';
  @Input() disabled = false;
  @Output() valueChange = new EventEmitter<string>();

  onInput(event: Event) {
    const input = event.target as HTMLInputElement;
    this.valueChange.emit(input.value);
  }
}