import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { CoursesService } from '../services/courses.service';
import { Lesson } from '../models/lesson';
import { SegmentResponse, CompleteSegmentResponse } from '../models/segment-response.model';
import { LessonViewerComponent } from "../shared/lesson-viewer.component";
import { EchoModalComponent } from "../components/echo-modal/echo-modal.component";
import { EchoStatePanelComponent } from '../components/echo-state-panel/echo-state-panel.component';
import { EchoLoadingStateComponent } from '../components/echo-loading-state/echo-loading-state.component';
import { StudentCourseWithDetails } from '../models/student-course-with-details.model';

@Component({
  selector: 'echoed-lesson-view',
  standalone: true,
  imports: [LessonViewerComponent, CommonModule, EchoModalComponent, EchoStatePanelComponent, EchoLoadingStateComponent],
  templateUrl: './lesson-view.component.html',
  styleUrl: './lesson-view.component.scss'
})
export class LessonViewComponent implements OnInit {
  unitProgressId!: string;
  segment?: SegmentResponse;
  lesson?: Lesson;
  courseCompleted = false;
  demoMode = false;
  loading = true;
  loadErrorMessage = '';
  completionErrorMessage = '';
  completingSegment = false;
  governedDeliveryState: SegmentResponse['delivery_state'] | null = null;
  governedDeliveryDetail = '';
  courseContextTitle = '';
  courseContextId = '';
  unitContextTitle = '';
  lessonPositionLabel = '';

  get governedStateTitle(): string {
    switch (this.governedDeliveryState) {
      case 'pending_review':
        return 'Lesson awaiting approval';
      case 'governed_unavailable':
        return 'Lesson unavailable right now';
      default:
        return 'Lesson delivery paused';
    }
  }

  get governedStateBody(): string {
    return this.governedDeliveryDetail || 'This lesson is not currently available for governed learner delivery. Return to your dashboard and try again later.';
  }

  get lessonActivityCount(): number {
    return this.lesson?.activities?.length || 0;
  }

  get lessonStatusLabel(): string {
    if (this.demoMode) {
      return 'Demo preview';
    }

    return 'Governed delivery';
  }

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
    this.loading = true;
    this.loadErrorMessage = '';
    this.coursesService.getCurrentSegment(this.unitProgressId).subscribe({
      next: (segment) => {
        this.segment = segment;
        if (segment.delivery_state !== 'governed_available' || !segment.lesson_id) {
          this.lesson = undefined;
          this.courseCompleted = segment.delivery_state === 'completed';
          this.governedDeliveryState = segment.delivery_state;
          this.governedDeliveryDetail = segment.detail || '';
          this.loading = false;
          return;
        }
        this.governedDeliveryState = null;
        this.governedDeliveryDetail = '';
        this.fetchLesson(segment.lesson_id);
      },
      error: (err) => {
        if (err?.status === 404) {
          this.recoverFromStaleSegment();
          return;
        }

        console.warn('Failed to restore the current governed lesson segment.', err);
        this.segment = undefined;
        this.lesson = undefined;
        this.courseCompleted = false;
        this.governedDeliveryState = null;
        this.governedDeliveryDetail = '';
        this.loadErrorMessage = 'We could not restore your lesson path right now. Retry to continue from your dashboard-safe progress point.';
        this.loading = false;
      }
    });
  }

  private recoverFromStaleSegment(): void {
    this.coursesService.getStudentCourses().subscribe({
      next: (studentCourses: StudentCourseWithDetails[]) => {
        const activeCourse = studentCourses.find((course) => course.unit_progress_id);
        const recoveredUnitProgressId = activeCourse?.unit_progress_id;

        if (!recoveredUnitProgressId || recoveredUnitProgressId === this.unitProgressId) {
          this.segment = undefined;
          this.lesson = undefined;
          this.courseCompleted = false;
          this.governedDeliveryState = null;
          this.governedDeliveryDetail = '';
          this.loadErrorMessage = 'We could not restore your lesson path right now. Retry to continue from your dashboard-safe progress point.';
          this.loading = false;
          return;
        }

        this.unitProgressId = recoveredUnitProgressId;
        this.router.navigate(['../', recoveredUnitProgressId], { relativeTo: this.route });
        this.loadSegmentAndLesson();
      },
      error: (err) => {
        console.warn('Failed to recover the governed lesson segment from student courses.', err);
        this.segment = undefined;
        this.lesson = undefined;
        this.courseCompleted = false;
        this.governedDeliveryState = null;
        this.governedDeliveryDetail = '';
        this.loadErrorMessage = 'We could not restore your lesson path right now. Retry to continue from your dashboard-safe progress point.';
        this.loading = false;
      }
    });
  }

  fetchLesson(lessonId: string): void {
    this.coursesService.getLessonById(lessonId).subscribe({
      next: (lesson) => {
        this.lesson = lesson;
        this.resolveLessonContext(lesson.id);
        this.loading = false;
      },
      error: (err) => {
        console.error('Error fetching lesson', err);
        this.lesson = undefined;
        const deliveryState = err?.error?.detail?.delivery_state;
        if (deliveryState) {
          this.governedDeliveryState = deliveryState;
          this.governedDeliveryDetail = err?.error?.detail?.message || 'This lesson is not currently available for governed learner delivery.';
        } else {
          this.governedDeliveryState = null;
          this.governedDeliveryDetail = '';
          this.loadErrorMessage = 'We could not load this lesson right now. Retry to restore your governed lesson view.';
        }
        this.loading = false;
      }
    });
  }

  onLessonCompleted(): void {
  if (this.demoMode) {
    this.courseCompleted = true;
    return;
  }
  if (this.completingSegment || !this.segment || !this.segment.lesson_id || !this.unitProgressId) {
    console.warn('Incomplete data to mark lesson complete');
    return;
  }

    this.completingSegment = true;
    this.completionErrorMessage = '';
    this.coursesService.markSegmentCompleted(this.unitProgressId, this.segment.lesson_id).subscribe({
    next: (res: CompleteSegmentResponse) => {
      this.completingSegment = false;
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
      this.completingSegment = false;
      this.completionErrorMessage = 'We could not save this lesson completion. Your lesson is still open, so try again before leaving.';
      console.error('Failed to mark segment complete:', err);
    }
  });
  }

  loadDemoLesson(): void {
    this.coursesService.getCourses().subscribe({
      next: (courses) => {
        const introCourse =
          courses.find((course) => {
            const pathwayKey = course.standards_metadata?.['pathway_key'];
            return pathwayKey === 'introduction-to-africa' || course.title === 'Introduction to Africa';
          }) || courses[0];

        if (!introCourse) {
          this.courseCompleted = true;
          return;
        }
        this.coursesService.getCourseById(introCourse.id).subscribe({
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
    this.router.navigate(['/learn']);
  }

  returnToCourse(): void {
    this.courseCompleted = false;
    if (this.courseContextId) {
      this.router.navigate(['/learn/courses', this.courseContextId]);
      return;
    }
    this.router.navigate(['/learn']);
  }

  retryLoad(): void {
    this.loadSegmentAndLesson();
  }

  private resolveLessonContext(lessonId: string): void {
    this.courseContextTitle = '';
    this.courseContextId = '';
    this.unitContextTitle = '';
    this.lessonPositionLabel = '';

    this.coursesService.getStudentCourses().subscribe({
      next: (studentCourses: StudentCourseWithDetails[]) => {
        for (const studentCourse of studentCourses) {
          const units = studentCourse.course.units || [];
          for (const unit of units) {
            const lessons = [...(unit.lessons || [])].sort((left, right) => {
              const leftOrder = left.order ?? Number.MAX_SAFE_INTEGER;
              const rightOrder = right.order ?? Number.MAX_SAFE_INTEGER;
              if (leftOrder !== rightOrder) {
                return leftOrder - rightOrder;
              }
              return left.title.localeCompare(right.title);
            });
            const lessonIndex = lessons.findIndex(lesson => lesson.id === lessonId);
            if (lessonIndex >= 0) {
              this.courseContextTitle = studentCourse.course.title;
              this.courseContextId = studentCourse.course_id;
              this.unitContextTitle = unit.title;
              this.lessonPositionLabel = `Lesson ${lessonIndex + 1} of ${lessons.length}`;
              return;
            }
          }
        }
      },
      error: () => {
        this.courseContextTitle = '';
        this.courseContextId = '';
        this.unitContextTitle = '';
        this.lessonPositionLabel = '';
      },
    });
  }

}
