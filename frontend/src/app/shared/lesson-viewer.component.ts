import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Lesson } from '../models/lesson';

@Component({
  selector: 'echoed-lesson-viewer',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './lesson-viewer.component.html',
  styleUrl: './lesson-viewer.component.scss'
})
export class LessonViewerComponent {
  @Input() lesson!: Lesson;
  @Input() isTeacherLed: boolean = false;
  @Output() segmentCompleted = new EventEmitter<void>();

  onMarkComplete(): void {
    // Emit when lesson segment is completed (for updating progress)
    this.segmentCompleted.emit();
  }
}
