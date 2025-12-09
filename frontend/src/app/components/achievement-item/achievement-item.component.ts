import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-achievement-item',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="bg-white p-4 rounded-xl shadow w-full flex items-center gap-3">
      <div class="text-2xl">{{ icon }}</div>
      <div>
        <p class="font-semibold text-primary text-sm">{{ title }}</p>
        <p class="text-xs text-gray-500">{{ description }}</p>
      </div>
    </div>
  `,
})
export class AchievementItemComponent {
  @Input() icon = '';
  @Input() title = '';
  @Input() description = '';
}
