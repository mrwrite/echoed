import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { Lesson } from '../models/lesson';

@Component({
  selector: 'echoed-lesson-viewer',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './lesson-viewer.component.html',
  styleUrl: './lesson-viewer.component.scss'
})
export class LessonViewerComponent {
  constructor(private sanitizer: DomSanitizer) {}

  @Input() lesson!: Lesson;
  @Input() isTeacherLed: boolean = false;
  @Output() segmentCompleted = new EventEmitter<void>();

  isYouTubeLink(url: string): boolean {
    return url.includes('youtube.com') || url.includes('youtu.be');
  }

  getYouTubeEmbedUrl(url: string): SafeResourceUrl {
    const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([\w-]+)/);
    const videoId = match && match[1] ? match[1] : '';
    return this.sanitizer.bypassSecurityTrustResourceUrl(`https://www.youtube.com/embed/${videoId}`);
  }

  onMarkComplete(): void {
    // Emit when lesson segment is completed (for updating progress)
    this.segmentCompleted.emit();
  }
}
