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
import { CompleteSegmentResponse } from '../../../models/segment-response.model';
import { ToastService } from '../../../services/toast.service';
import { AnalyticsService, StudentProgressResponse } from '../../../services/analytics.service';
import { BadgesService } from '../../../services/badges.service';
import { StudentBadge } from '../../../models/badge';
import { Program, StudentCertification } from '../../../models/program';
import { ProgramsService } from '../../../services/programs.service';

@Component({
  selector: 'echoed-student-view',
  standalone: true,
  imports: [
    CommonModule,
    LessonViewerComponent,
    EchoButtonComponent,
    StudentCourseCardComponent,
  ],
  templateUrl: './student-view.component.html',
  styleUrl: './student-view.component.scss'
})
export class StudentViewComponent implements OnInit {
  @Input() userInfo!: UserInfo;
  studentCourses: StudentCourseWithDetails[] = [];
  activeStudentCourse?: StudentCourseWithDetails;
  currentLesson?: Lesson;
  showLesson = false;
  availableCourses: Course[] = [];
  badgeProgress: StudentProgressResponse['badge_progress'] = [];
  studentBadges: StudentBadge[] = [];
  programs: Program[] = [];
  certifications: StudentCertification[] = [];
  streakDays = 0;
  lessonsCompleted = 0;
  unitsCompleted = 0;
  coursesCompleted = 0;
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
    this.coursesService.getStudentCourses().subscribe({
    next: (courses) => {
      this.studentCourses = courses;

      this.activeStudentCourse = this.studentCourses[0];

      // Calculate progress for each enrolled course
      this.studentCourses.forEach(sc => {
        this.coursesService.getCourseProgress(sc).subscribe(progress => {
          sc.progress = progress;
        });
      });

      this.loadAvailableCourses(); // Refresh available courses after loading student courses
    },
    error: (err) => {
      console.error('Failed to load student courses', err);
    }
  });
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
          if (nextSeg && nextSeg.unit_progress_id) {
            this.activeStudentCourse!.unit_progress_id = nextSeg.unit_progress_id;
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
      this.router.navigate(['/home/lesson', segment.unit_progress_id || '']);
    });
  }

  goToPrograms(): void {
    this.router.navigate(['/home/programs']);
  }

  goToCertifications(): void {
    this.router.navigate(['/home/certifications']);
  }
}
