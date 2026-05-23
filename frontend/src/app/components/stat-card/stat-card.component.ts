import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IconModule } from '../../shared/icon/icon.module';

@Component({
  selector: 'app-stat-card',
  standalone: true,
  imports: [CommonModule, IconModule],
  template: `
    <div class="bg-white p-6 rounded-xl shadow flex flex-col space-y-1">
      <div class="flex items-start space-x-2">
        <span
          aria-hidden="true"
          class="inline-block h-6 w-6 flex-shrink-0 rounded-full bg-current opacity-70"
        ></span>
        <div class="flex flex-col">
          <p class="text-2xl font-bold text-[#1A1A40]">{{ value }}</p>
          <p class="text-gray-500 tracking-tight leading-snug">{{ label }}</p>
        </div>
      </div>
    </div>
  `,
})
export class StatCardComponent {
  @Input() icon: string = 'User';
  @Input() label: string = '';
  @Input() value: number | string = 0;
}
