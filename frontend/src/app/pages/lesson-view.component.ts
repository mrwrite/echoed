import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { CoursesService } from '../services/courses.service';
import { Lesson } from '../models/lesson';
import { SegmentResponse, CompleteSegmentResponse } from '../models/segment-response.model';
import { LessonViewerComponent } from "../shared/lesson-viewer.component";
import { EchoModalComponent } from "../components/echo-modal/echo-modal.component";

@Component({
  selector: 'echoed-lesson-view',
  standalone: true,
  imports: [LessonViewerComponent, CommonModule, EchoModalComponent],
  templateUrl: './lesson-view.component.html',
  styleUrl: './lesson-view.component.scss'
})
export class LessonViewComponent implements OnInit {
  unitProgressId!: string;
  segment?: SegmentResponse;
  lesson?: Lesson;
  courseCompleted = false;
  demoMode = false;
  governedDeliveryState: SegmentResponse['delivery_state'] | null = null;
  governedDeliveryDetail = '';

  constructor(
    private route: ActivatedRoute,
    private coursesService: CoursesService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.unitProgressId = this.route.snapshot.paramMap.get('id')!;
    if (this.unitProgressId === 'demo') {
      this.demoMode = true;
      this.loadDemoLesson();
      return;
    }
    this.loadSegmentAndLesson();
  }

  loadSegmentAndLesson(): void {
    this.coursesService.getCurrentSegment(this.unitProgressId).subscribe({
      next: (segment) => {
        this.segment = segment;
        if (segment.delivery_state !== 'governed_available' || !segment.lesson_id) {
          this.lesson = undefined;
          this.courseCompleted = segment.delivery_state === 'completed';
          this.governedDeliveryState = segment.delivery_state;
          this.governedDeliveryDetail = segment.detail || '';
          return;
        }
        this.governedDeliveryState = null;
        this.governedDeliveryDetail = '';
        this.fetchLesson(segment.lesson_id);
      },
      error: (err) => {
          console.warn('All segments may be complete or none found.', err);
          this.segment = undefined;
          this.lesson = undefined;
          this.courseCompleted = true;
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
        this.lesson = undefined;
        this.governedDeliveryState = err?.error?.detail?.delivery_state || 'governed_unavailable';
        this.governedDeliveryDetail = err?.error?.detail?.message || 'This lesson is not currently available for governed learner delivery.';
      }
    });
  }

  onLessonCompleted(): void {
  if (this.demoMode) {
    this.courseCompleted = true;
    return;
  }
  if (!this.segment || !this.segment.lesson_id || !this.unitProgressId) {
    console.warn('Incomplete data to mark lesson complete');
    return;
  }

    this.coursesService.markSegmentCompleted(this.unitProgressId, this.segment.lesson_id).subscribe({
    next: (res: CompleteSegmentResponse) => {
      const nextSeg = res.next_segment;
      if (nextSeg.delivery_state === 'governed_available' && nextSeg.lesson_id) {
        if (nextSeg.unit_progress_id) {
          this.unitProgressId = nextSeg.unit_progress_id;
        }
        this.segment = nextSeg;
        this.governedDeliveryState = null;
        this.governedDeliveryDetail = '';
        this.fetchLesson(nextSeg.lesson_id);
      } else if (nextSeg.delivery_state === 'completed') {
        this.segment = undefined;
        this.lesson = undefined;
        this.courseCompleted = true;
      } else {
        this.segment = undefined;
        this.lesson = undefined;
        this.courseCompleted = false;
        this.governedDeliveryState = nextSeg.delivery_state;
        this.governedDeliveryDetail = nextSeg.detail || '';
      }
    },
    error: (err) => {
      console.error('Failed to mark segment complete:', err);
    }
  });
  }

  loadDemoLesson(): void {
    this.coursesService.getCourses().subscribe({
      next: (courses) => {
        const firstCourse = courses[0];
        if (!firstCourse) {
          this.courseCompleted = true;
          return;
        }
        this.coursesService.getCourseById(firstCourse.id).subscribe({
          next: (course) => {
            const firstUnit = course.units?.[0];
            const firstLesson = firstUnit?.lessons?.[0];
            if (firstLesson) {
              this.lesson = firstLesson as Lesson;
            } else {
              this.courseCompleted = true;
            }
          },
          error: () => {
            this.courseCompleted = true;
          }
        });
      },
      error: () => {
        this.courseCompleted = true;
      }
    });
  }

  returnToDashboard(): void {
    this.courseCompleted = false;
    this.router.navigate(['/home']);
  }

}
