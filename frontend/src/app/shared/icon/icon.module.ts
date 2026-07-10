import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

type IconPathMap = Record<string, string[]>;

const ICON_PATHS: IconPathMap = {
  Award: [
    'M12 15.5a5.5 5.5 0 1 0 0-11 5.5 5.5 0 0 0 0 11Z',
    'M8.5 14.5 7 22l5-3 5 3-1.5-7.5',
  ],
  Book: [
    'M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21.5v-16Z',
    'M4 5.5A2.5 2.5 0 0 1 6.5 8H20',
  ],
  BookOpen: [
    'M4 5.5A2.5 2.5 0 0 1 6.5 3H11v17H6.5A2.5 2.5 0 0 0 4 22V5.5Z',
    'M20 5.5A2.5 2.5 0 0 0 17.5 3H13v17h4.5A2.5 2.5 0 0 1 20 22V5.5Z',
  ],
  ClipboardList: [
    'M9 4h6a2 2 0 0 1 2 2v1H7V6a2 2 0 0 1 2-2Z',
    'M8 6H6a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-2',
    'M8 12h8M8 16h8',
  ],
  FileText: [
    'M6 3h8l4 4v14H6V3Z',
    'M14 3v5h5',
    'M8 13h8M8 17h6',
  ],
  Home: [
    'M3 11.5 12 4l9 7.5',
    'M5 10.5V21h5v-6h4v6h5V10.5',
  ],
  Menu: [
    'M4 6h16',
    'M4 12h16',
    'M4 18h16',
  ],
  Settings: [
    'M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z',
    'M19.4 15a1.7 1.7 0 0 0 .34 1.87l.04.04a2 2 0 0 1-2.83 2.83l-.04-.04a1.7 1.7 0 0 0-1.87-.34 1.7 1.7 0 0 0-1.04 1.56V21a2 2 0 0 1-4 0v-.06a1.7 1.7 0 0 0-1.04-1.56 1.7 1.7 0 0 0-1.87.34l-.04.04a2 2 0 0 1-2.83-2.83l.04-.04A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.56-1.04H3a2 2 0 0 1 0-4h.06A1.7 1.7 0 0 0 4.6 8.92a1.7 1.7 0 0 0-.34-1.87l-.04-.04a2 2 0 0 1 2.83-2.83l.04.04a1.7 1.7 0 0 0 1.87.34A1.7 1.7 0 0 0 10 3.06V3a2 2 0 0 1 4 0v.06a1.7 1.7 0 0 0 1.04 1.56 1.7 1.7 0 0 0 1.87-.34l.04-.04a2 2 0 0 1 2.83 2.83l-.04.04a1.7 1.7 0 0 0-.34 1.87 1.7 1.7 0 0 0 1.56 1.04H21a2 2 0 0 1 0 4h-.06A1.7 1.7 0 0 0 19.4 15Z',
  ],
  SlidersHorizontal: [
    'M4 7h4M12 7h8',
    'M4 17h10M18 17h2',
    'M8 10a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z',
    'M16 20a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z',
  ],
  User: [
    'M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z',
    'M4 21a8 8 0 0 1 16 0',
  ],
  Users: [
    'M9 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z',
    'M2 21a7 7 0 0 1 14 0',
    'M17 11a3 3 0 1 0 0-6',
    'M17 15a5.5 5.5 0 0 1 5 6',
  ],
};

@Component({
  selector: 'app-icon',
  standalone: false,
  template: `
    <svg
      aria-hidden="true"
      focusable="false"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-linecap="round"
      stroke-linejoin="round"
      [attr.stroke-width]="strokeWidth"
      [style.width.px]="size"
      [style.height.px]="size"
    >
      <path *ngFor="let path of paths" [attr.d]="path"></path>
    </svg>
  `,
})
export class AppIconComponent {
  @Input() name = 'FileText';
  @Input() size = 20;
  @Input() strokeWidth = 2;

  get paths(): string[] {
    return ICON_PATHS[this.name] || ICON_PATHS['FileText'];
  }
}

@NgModule({
  declarations: [AppIconComponent],
  imports: [CommonModule],
  exports: [AppIconComponent],
})
export class IconModule {}
