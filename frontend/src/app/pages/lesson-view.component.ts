import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { CoursesService } from '../services/courses.service';
import { Lesson } from '../models/lesson';
import { SegmentResponse } from '../models/segment-response.model';
import { LessonViewerComponent } from "../shared/lesson-viewer.component";

@Component({
  selector: 'echoed-lesson-view',
  standalone: true,
  imports: [LessonViewerComponent, CommonModule],
  templateUrl: './lesson-view.component.html',
  styleUrl: './lesson-view.component.scss'
})
export class LessonViewComponent implements OnInit {
  unitProgressId!: string;
  segment?: SegmentResponse;
  lesson?: Lesson;

  constructor(
    private route: ActivatedRoute,
    private coursesService: CoursesService
  ) {}

  ngOnInit(): void {
    this.unitProgressId = this.route.snapshot.paramMap.get('id')!;
    this.loadSegmentAndLesson();
  }

  loadSegmentAndLesson(): void {
    this.coursesService.getCurrentSegment(this.unitProgressId).subscribe({
      next: (segment) => {
        this.segment = segment;
        this.fetchLesson(segment.lesson_id);
      },
      error: (err) => {
          console.warn('All segments may be complete or none found.', err);
          this.segment = undefined;
          this.lesson = undefined;
      }
    });
  }

  fetchLesson(lessonId: string): void {
    this.coursesService.getLessonById(lessonId).subscribe({
      next: (lesson) => {
        this.lesson = lesson;
      },
      error: (err) => {
        console.error('Error fetching lesson', err);
      }
    });
  }

  onLessonCompleted(): void {
  if (!this.segment || !this.segment.lesson_id || !this.unitProgressId) {
    console.warn('Incomplete data to mark lesson complete');
    return;
  }

  this.coursesService.markSegmentCompleted(this.unitProgressId, this.segment.lesson_id).subscribe({
    next: () => {
      console.log('Lesson marked complete');
      this.loadSegmentAndLesson(); // Reload to update segment status
    },
    error: (err) => {
      console.error('Failed to mark segment complete:', err);
    }
  });
}

}
