import { Component, Input, Output, EventEmitter, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { Lesson } from '../models/lesson';
import { ColoringCanvasComponent } from '../components/coloring-canvas/coloring-canvas.component';
import { StorybookViewerComponent } from '../components/storybook-viewer/storybook-viewer.component';

@Component({
  selector: 'echoed-lesson-viewer',
  standalone: true,
  imports: [CommonModule, FormsModule, ColoringCanvasComponent, StorybookViewerComponent],
  templateUrl: './lesson-viewer.component.html',
  styleUrl: './lesson-viewer.component.scss'
})
export class LessonViewerComponent implements OnChanges {
  constructor(private sanitizer: DomSanitizer) {}

  @Input() lesson!: Lesson;
  @Input() isTeacherLed: boolean = false;
  @Output() segmentCompleted = new EventEmitter<void>();

  currentActivityIndex = 0;
  reflectionResponse = '';
  selectedOption = '';

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['lesson']) {
      this.currentActivityIndex = 0;
      this.reflectionResponse = '';
      this.selectedOption = '';
    }
  }

  get currentActivity() {
    return this.lesson?.activities[this.currentActivityIndex];
  }

  goToNextActivity(): void {
    if (this.lesson && this.currentActivityIndex < this.lesson.activities.length - 1) {
      this.currentActivityIndex++;
      this.reflectionResponse = '';
      this.selectedOption = '';
    }
  }

  isYouTubeLink(url: string): boolean {
    return url.includes('youtube.com') || url.includes('youtu.be');
  }

  getYouTubeEmbedUrl(url: string): SafeResourceUrl {
    const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([\w-]+)/);
    const videoId = match && match[1] ? match[1] : '';
    return this.sanitizer.bypassSecurityTrustResourceUrl(`https://www.youtube.com/embed/${videoId}`);
  }

  get quizPayload() {
    const content = this.currentActivity?.content;
    if (!content) {
      return null;
    }
    try {
      const parsed = JSON.parse(content);
      if (parsed && parsed.question && Array.isArray(parsed.options)) {
        return parsed;
      }
    } catch {
      return null;
    }
    return null;
  }

  onMarkComplete(): void {
    // Emit when lesson segment is completed (for updating progress)
    this.segmentCompleted.emit();
  }
}
