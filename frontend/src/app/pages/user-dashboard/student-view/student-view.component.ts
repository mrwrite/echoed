import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UserInfo } from '../../../models/user-info';
import { CoursesService } from '../../../services/courses.service';
import { Router } from '@angular/router';
import { Lesson } from '../../../models/lesson';
import { LessonViewerComponent } from "../../../shared/lesson-viewer.component";
import { EchoButtonComponent } from '../../../components/echo-button/echo-button.component';
import { StudentCourseCardComponent } from '../../../components/student-course-card/student-course-card.component';
import { Course } from '../../../models/course';
import { StudentCourseWithDetails } from '../../../models/student-course-with-details.model';
import { CompleteSegmentResponse, SegmentResponse } from '../../../models/segment-response.model';
import { ToastService } from '../../../services/toast.service';
import { AnalyticsService, StudentProgressResponse } from '../../../services/analytics.service';
import { BadgesService } from '../../../services/badges.service';
import { StudentBadge } from '../../../models/badge';
import { Program, StudentCertification } from '../../../models/program';
import { ProgramsService } from '../../../services/programs.service';
import { EchoStatePanelComponent } from '../../../components/echo-state-panel/echo-state-panel.component';
import { EchoLoadingStateComponent } from '../../../components/echo-loading-state/echo-loading-state.component';

@Component({
  selector: 'echoed-student-view',
  standalone: true,
  imports: [
    CommonModule,
    LessonViewerComponent,
    EchoButtonComponent,
    StudentCourseCardComponent,
    EchoStatePanelComponent,
    EchoLoadingStateComponent,
  ],
  templateUrl: './student-view.component.html',
  styleUrl: './student-view.component.scss'
})
export class StudentViewComponent implements OnInit {
  @Input() userInfo!: UserInfo;
  studentCourses: StudentCourseWithDetails[] = [];
  activeStudentCourse?: StudentCourseWithDetails;
  activeStudentCourseReason = '';
  currentLesson?: Lesson;
  showLesson = false;
  availableCourses: Course[] = [];
  badgeProgress: StudentProgressResponse['badge_progress'] = [];
  studentBadges: StudentBadge[] = [];
  programs: Program[] = [];
  certifications: StudentCertification[] = [];
  governedDeliveryState: SegmentResponse['delivery_state'] | null = null;
  governedDeliveryDetail = '';
  streakDays = 0;
  lessonsCompleted = 0;
  unitsCompleted = 0;
  coursesCompleted = 0;
  coursesLoading = true;
  coursesLoadError = '';
  /** Number of courses shown initially before "View More" is clicked */
  availableCoursesVisibleCount = 4;
  demoTimeline = [
    { label: 'Yesterday', detail: 'Completed “Roots of Rhythm” lesson', status: 'completed' },
    { label: 'Today', detail: 'Continue African kingdoms storytelling', status: 'active' },
    { label: 'Next', detail: 'Interactive map: The Trans-Saharan routes', status: 'upcoming' }
  ];

  get visibleAvailableCourses(): Course[] {
    return this.availableCourses.slice(0, this.availableCoursesVisibleCount);
  }

  /** Navigate to the full available courses page */
  goToAvailableCourses(): void {
    this.router.navigate(['/home/courses']);
  }
  

  constructor(private coursesService: CoursesService,
              private router: Router,
              private toastService: ToastService,
              private analyticsService: AnalyticsService,
              private badgesService: BadgesService,
              private programsService: ProgramsService
  ) { }

  ngOnInit(): void {
    this.loadStudentCourses();
    this.loadProgressInsights();
    this.loadBadges();
    this.loadProgramsOverview();
  }

  loadProgressInsights(): void {
    this.analyticsService.getStudentProgress().subscribe({
      next: (progress) => {
        this.badgeProgress = progress.badge_progress;
        this.streakDays = progress.metrics.streak_days;
        this.lessonsCompleted = progress.metrics.lessons_completed;
        this.unitsCompleted = progress.metrics.units_completed;
        this.coursesCompleted = progress.metrics.courses_completed;
      },
      error: (err) => {
        console.error('Failed to load progress insights', err);
      }
    });
  }

  loadBadges(): void {
    if (!this.userInfo?.user_id) {
      return;
    }
    this.badgesService.getStudentBadges(this.userInfo.user_id).subscribe({
      next: (badges) => {
        this.studentBadges = badges;
      },
      error: (err) => {
        console.error('Failed to load badges', err);
      }
    });
  }

  loadProgramsOverview(): void {
    this.programsService.getPrograms().subscribe({
      next: (programs) => {
        this.programs = programs;
      },
      error: (err) => {
        console.error('Failed to load programs', err);
      }
    });

    this.programsService.getMyCertifications().subscribe({
      next: (certifications) => {
        this.certifications = certifications;
      },
      error: (err) => {
        console.error('Failed to load certifications', err);
      }
    });
  }

  loadAvailableCourses(): void {
  this.coursesService.getCourses().subscribe({
    next: (courses) => {
      const enrolledCourseIds = this.studentCourses.map(sc => sc.course_id);
      this.availableCourses = courses.filter(course => !enrolledCourseIds.includes(course.id));
    },
    error: (err) => {
      console.error('Failed to load available courses', err);
    }
  });
}

  loadStudentCourses(): void {
    this.coursesLoading = true;
    this.coursesLoadError = '';
    this.coursesService.getStudentCourses().subscribe({
    next: (courses) => {
      this.studentCourses = courses;
      this.resolveContinuationCourse();

      // Calculate progress for each enrolled course
      this.studentCourses.forEach(sc => {
        this.coursesService.getCourseProgress(sc).subscribe(progress => {
          sc.progress = progress;
        });
      });

      this.loadAvailableCourses(); // Refresh available courses after loading student courses
      this.coursesLoading = false;
    },
    error: (err) => {
      console.error('Failed to load student courses', err);
      this.studentCourses = [];
      this.activeStudentCourse = undefined;
      this.activeStudentCourseReason = '';
      this.availableCourses = [];
      this.coursesLoadError = 'We could not load your learning dashboard right now. Retry to restore your active courses and continuation path.';
      this.coursesLoading = false;
    }
  });
  }

  private resolveContinuationCourse(): void {
    const inProgressStatuses = new Set(['active', 'in_progress', 'in-progress']);
    const inProgressCourse = this.studentCourses.find((course) =>
      inProgressStatuses.has((course.status || '').toLowerCase())
      || ((course.progress ?? 0) > 0 && course.status !== 'completed')
    );

    if (inProgressCourse) {
      this.activeStudentCourse = inProgressCourse;
      this.activeStudentCourseReason = 'Continue where you already have momentum.';
      return;
    }

    const nextAvailableCourse = [...this.studentCourses]
      .filter((course) => course.status !== 'completed')
      .sort((left, right) => {
        const leftDate = Date.parse(left.enrolled_on || '') || 0;
        const rightDate = Date.parse(right.enrolled_on || '') || 0;
        if (leftDate !== rightDate) {
          return leftDate - rightDate;
        }

        return left.course.title.localeCompare(right.course.title);
      })[0];

    if (nextAvailableCourse) {
      this.activeStudentCourse = nextAvailableCourse;
      this.activeStudentCourseReason = 'Next recommended course based on your enrolled learning path.';
      return;
    }

    this.activeStudentCourse = undefined;
    this.activeStudentCourseReason = '';
  }

  onLessonCompleted(): void {
  if (!this.currentLesson || !this.activeStudentCourse) return;

  if (this.activeStudentCourse.unit_progress_id) {
    this.coursesService
      .markSegmentCompleted(
        this.activeStudentCourse.unit_progress_id,
        this.currentLesson.id
      )
      .subscribe({
        next: (res: CompleteSegmentResponse) => {
          const nextSeg = res.next_segment;
          if (nextSeg.delivery_state === 'governed_available' && nextSeg.unit_progress_id) {
            this.activeStudentCourse!.unit_progress_id = nextSeg.unit_progress_id;
          } else if (nextSeg.delivery_state !== 'completed') {
            this.governedDeliveryState = nextSeg.delivery_state;
            this.governedDeliveryDetail = nextSeg.detail || 'This lesson path is not currently available.';
            this.toastService.show(this.governedDeliveryDetail, 'error');
          }
          this.toastService.show('Lesson completed! Progress saved.', 'success');
          this.showLesson = false;
          this.currentLesson = undefined;
          this.loadStudentCourses();
          this.loadProgressInsights();
          this.loadBadges();
          this.loadProgramsOverview();
        },
        error: () => {
          this.toastService.show('There was an error saving your progress.', 'error');
        },
      });
  }
}

enrollInCourse(courseId: string): void {
  this.coursesService.enrollInCourse(courseId).subscribe({
    next: () => {
      this.toastService.show('Enrollment successful!', 'success');
      this.loadStudentCourses();
      this.loadAvailableCourses();
    },
    error: (err) => {
      console.error('Enrollment failed', err);
      this.toastService.show('Enrollment failed. You may already be enrolled.', 'error');
    }
  });
}


  startCourse(course: StudentCourseWithDetails): void {
    this.coursesService.startCourse({ course_id: course.course.id }).subscribe(segment => {
      if (segment.delivery_state === 'governed_available' && segment.unit_progress_id) {
        this.governedDeliveryState = null;
        this.governedDeliveryDetail = '';
        this.router.navigate(['/home/lesson', segment.unit_progress_id]);
        return;
      }

      this.governedDeliveryState = segment.delivery_state;
      this.governedDeliveryDetail = segment.detail || 'This course is not currently available for governed learner delivery.';
      this.toastService.show(this.governedDeliveryDetail, 'error');
    });
  }

  goToPrograms(): void {
    this.router.navigate(['/home/programs']);
  }

  goToCertifications(): void {
    this.router.navigate(['/home/certifications']);
  }

  retryCourseLoad(): void {
    this.loadStudentCourses();
  }
}
