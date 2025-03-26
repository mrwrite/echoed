import { Component, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-echo-checkbox',
  standalone: true,
  template: `
    <label class="inline-flex items-center cursor-pointer">
      <input
        type="checkbox"
        class="form-checkbox w-5 h-5 text-primary border-gray-300 rounded focus:ring-primary"
        [checked]="checked"
        (change)="onToggle($event)"
      />
      <span class="ml-2 text-sm font-medium">{{ label }}</span>
    </label>
  `,
})
export class EchoCheckboxComponent {
  @Input() label: string = 'Checkbox';
  @Input() checked: boolean = false;
  @Output() checkedChange = new EventEmitter<boolean>();

  onToggle(event: Event) {
    const input = event.target as HTMLInputElement;
    this.checkedChange.emit(input.checked);
  }
}
