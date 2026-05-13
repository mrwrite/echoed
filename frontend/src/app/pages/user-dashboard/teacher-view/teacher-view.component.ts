import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { UserInfo } from '../../../models/user-info';
import { CoursesService } from '../../../services/courses.service';
import { Course } from '../../../models/course';
import { CoursePublishReadiness, CourseSafePublishValidation } from '../../../models/course-publish-readiness.model';
import { IconModule } from '../../../shared/icon/icon.module';
import { ToastService } from '../../../services/toast.service';
import {
  AnalyticsService,
  EducatorRuntimeSupportSummary,
  TeacherSummaryRow,
} from '../../../services/analytics.service';
import { UsersService } from '../../../services/users.service';
import { User } from '../../../models/user';
import { EchoStatePanelComponent } from '../../../components/echo-state-panel/echo-state-panel.component';
import { EchoLoadingStateComponent } from '../../../components/echo-loading-state/echo-loading-state.component';
import { forkJoin } from 'rxjs';

@Component({
  selector: 'echoed-teacher-view',
  standalone: true,
  imports: [CommonModule, FormsModule, IconModule, EchoStatePanelComponent, EchoLoadingStateComponent],
  templateUrl: './teacher-view.component.html',
  styleUrl: './teacher-view.component.scss'
})
export class TeacherViewComponent implements OnInit {
  @Input() userInfo!: UserInfo;
  private readonly flagshipPathwayKey = 'introduction-to-africa';

  courses: Course[] = [];
  readonly visibleCount = 5;
  students: User[] = [];
  teacherSummary: TeacherSummaryRow[] = [];
  educatorRuntimeSupport: EducatorRuntimeSupportSummary[] = [];
  selectedCourseId = '';
  selectedStudentId = '';
  coursesLoading = true;
  studentsLoading = true;
  summaryLoading = true;
  runtimeSupportLoading = true;
  publishReadinessLoading = true;
  safePublishLoading = true;
  coursesError = '';
  studentsError = '';
  summaryError = '';
  runtimeSupportError = '';
  publishReadinessError = '';
  safePublishError = '';
  courseReadiness: CoursePublishReadiness[] = [];
  safePublishValidations: CourseSafePublishValidation[] = [];

  constructor(
    private coursesService: CoursesService,
    private router: Router,
    private toastService: ToastService,
    private analyticsService: AnalyticsService,
    private usersService: UsersService,
  ) {}

  ngOnInit(): void {
    this.loadCourses();
    this.loadStudents();
    this.loadTeacherSummary();
  }

  get visibleCourses(): Course[] {
    return this.courses.slice(0, this.visibleCount);
  }

  get inProgressLessons(): number {
    return this.teacherSummary.filter(row => row.status === 'active').length;
  }

  get averageCompletion(): number {
    if (this.teacherSummary.length === 0) {
      return 0;
    }
    const total = this.teacherSummary.reduce((sum, row) => sum + row.progress, 0);
    return Math.round(total / this.teacherSummary.length);
  }

  get quickActionsLoading(): boolean {
    return this.coursesLoading || this.studentsLoading;
  }

  get quickActionsError(): string {
    return this.coursesError || this.studentsError;
  }

  get flagshipCourse(): Course | undefined {
    return this.courses.find((course) => {
      const pathwayKey = course.standards_metadata?.['pathway_key'];
      return pathwayKey === this.flagshipPathwayKey || course.title === 'Introduction to Africa';
    });
  }

  get runtimeSupportStateLabel(): Record<string, string> {
    return {
      remediation: 'Needs review support',
      enrichment: 'Ready for enrichment',
      normal: 'Continuing normally',
      completed: 'Completed pathway',
      unknown: 'Support state unknown',
    };
  }

  get runtimeSupportSectionEmpty(): boolean {
    return !this.runtimeSupportLoading && !this.runtimeSupportError && this.educatorRuntimeSupport.length === 0;
  }

  get publishReadinessSectionEmpty(): boolean {
    return !this.publishReadinessLoading && !this.publishReadinessError && this.courseReadiness.length === 0;
  }

  get safePublishSectionEmpty(): boolean {
    return !this.safePublishLoading && !this.safePublishError && this.safePublishValidations.length === 0;
  }

  loadCourses(): void {
    this.coursesLoading = true;
    this.coursesError = '';
    this.coursesService.getCourses().subscribe({
      next: (courses) => {
        this.courses = courses;
        this.coursesLoading = false;
        this.loadCoursePublishReadiness();
        this.loadEducatorRuntimeSupport();
      },
      error: () => {
        this.courses = [];
        this.coursesLoading = false;
        this.coursesError = 'We could not load educator courses right now. Retry to restore course management.';
        this.runtimeSupportLoading = false;
        this.educatorRuntimeSupport = [];
        this.publishReadinessLoading = false;
        this.courseReadiness = [];
        this.publishReadinessError = '';
        this.safePublishLoading = false;
        this.safePublishValidations = [];
        this.safePublishError = '';
      },
    });
  }

  loadStudents(): void {
    this.studentsLoading = true;
    this.studentsError = '';
    this.usersService.getStudents().subscribe({
      next: (students) => {
        this.students = students;
        this.studentsLoading = false;
      },
      error: () => {
        this.students = [];
        this.studentsLoading = false;
        this.studentsError = 'We could not load learner roster data right now. Retry to restore course assignment.';
      },
    });
  }

  loadTeacherSummary(): void {
    this.summaryLoading = true;
    this.summaryError = '';
    this.analyticsService.getTeacherSummary().subscribe({
      next: (summary) => {
        this.teacherSummary = summary;
        this.summaryLoading = false;
      },
      error: () => {
        this.teacherSummary = [];
        this.summaryLoading = false;
        this.summaryError = 'We could not load learner progress right now. Retry to restore the latest classroom summary.';
      },
    });
  }

  loadEducatorRuntimeSupport(): void {
    const flagshipCourse = this.flagshipCourse;
    this.runtimeSupportLoading = true;
    this.runtimeSupportError = '';

    if (!flagshipCourse) {
      this.educatorRuntimeSupport = [];
      this.runtimeSupportLoading = false;
      return;
    }

    this.analyticsService.getEducatorRuntimeSupport(flagshipCourse.id).subscribe({
      next: (rows) => {
        this.educatorRuntimeSupport = rows;
        this.runtimeSupportLoading = false;
      },
      error: () => {
        this.educatorRuntimeSupport = [];
        this.runtimeSupportLoading = false;
        this.runtimeSupportError = 'We could not load runtime learner support right now. Retry to restore remediation and enrichment visibility.';
      },
    });
  }

  supportStateClasses(state: string): string {
    switch (state) {
      case 'remediation':
        return 'bg-amber-100 text-amber-900 border border-amber-200';
      case 'enrichment':
        return 'bg-emerald-100 text-emerald-900 border border-emerald-200';
      case 'completed':
        return 'bg-sky-100 text-sky-900 border border-sky-200';
      case 'normal':
        return 'bg-slate-100 text-slate-800 border border-slate-200';
      default:
        return 'bg-white text-slate-700 border border-slate-200';
    }
  }

  readinessStateClasses(isReady: boolean): string {
    return isReady
      ? 'bg-emerald-100 text-emerald-900 border border-emerald-200'
      : 'bg-amber-100 text-amber-900 border border-amber-200';
  }

  readinessStateLabel(isReady: boolean): string {
    return isReady ? 'Ready' : 'Not ready';
  }

  safePublishStateLabel(isSafe: boolean): string {
    return isSafe ? 'Safe' : 'Not safe';
  }

  loadCoursePublishReadiness(): void {
    this.publishReadinessLoading = true;
    this.publishReadinessError = '';

    if (this.visibleCourses.length === 0) {
      this.courseReadiness = [];
      this.publishReadinessLoading = false;
      this.safePublishValidations = [];
      this.safePublishLoading = false;
      this.safePublishError = '';
      return;
    }

    forkJoin(
      this.visibleCourses.map((course) => this.coursesService.getCoursePublishReadiness(course.id)),
    ).subscribe({
      next: (readiness) => {
        this.courseReadiness = readiness;
        this.publishReadinessLoading = false;
        this.loadCourseSafePublishValidation();
      },
      error: () => {
        this.courseReadiness = [];
        this.publishReadinessLoading = false;
        this.publishReadinessError = 'We could not load course publish readiness right now. Retry to restore governance checks.';
        this.safePublishValidations = [];
        this.safePublishLoading = false;
        this.safePublishError = '';
      },
    });
  }

  loadCourseSafePublishValidation(): void {
    this.safePublishLoading = true;
    this.safePublishError = '';

    if (this.visibleCourses.length === 0) {
      this.safePublishValidations = [];
      this.safePublishLoading = false;
      return;
    }

    forkJoin(
      this.visibleCourses.map((course) => this.coursesService.getCourseSafePublishValidation(course.id)),
    ).subscribe({
      next: (validations) => {
        this.safePublishValidations = validations;
        this.safePublishLoading = false;
      },
      error: () => {
        this.safePublishValidations = [];
        this.safePublishLoading = false;
        this.safePublishError = 'We could not load course safe-publish validation right now. Retry to restore learner-safety checks.';
      },
    });
  }

  onAddCourse() {
    this.router.navigate(['/home/courses/new']);
  }

  onManageCourse(courseId: string) {
    this.router.navigate(['/home/courses', courseId, 'edit']);
  }

  deleteCourse(courseId: string) {
    this.coursesService.deleteCourse(courseId).subscribe({
      next: () => {
        this.courses = this.courses.filter(c => c.id !== courseId);
        this.courseReadiness = this.courseReadiness.filter((readiness) => readiness.course_id !== courseId);
        this.safePublishValidations = this.safePublishValidations.filter((validation) => validation.course_id !== courseId);
      },
      error: () => {
        this.toastService.show('We could not delete that course right now.', 'error');
      },
    });
  }

  viewAllCourses() {
    this.router.navigate(['/home/admin/courses']);
  }

  assignCourse() {
    if (!this.selectedCourseId || !this.selectedStudentId) {
      this.toastService.show('Select a student and a course to assign.', 'info');
      return;
    }
    this.coursesService.assignCourseToStudent(this.selectedCourseId, this.selectedStudentId).subscribe({
      next: () => {
        this.toastService.show('Course assigned successfully.', 'success');
        this.selectedCourseId = '';
        this.selectedStudentId = '';
        this.loadTeacherSummary();
      },
      error: (err) => {
        this.toastService.show(err?.error?.detail || 'Assignment failed.', 'error');
      }
    });
  }

  startLiveLesson() {
    const targetCourse = this.courses[0];
    if (targetCourse) {
      this.router.navigate(['/home/lesson', 'demo']);
    } else {
      this.toastService.show('Add a course first to start a live lesson.', 'info');
    }
  }

  viewReports() {
    this.toastService.show('Reports are listed in the Student Progress table.', 'info');
  }

  retryCourses(): void {
    this.loadCourses();
  }

  retryPublishReadiness(): void {
    if (this.coursesLoading) {
      return;
    }
    this.loadCoursePublishReadiness();
  }

  retrySafePublish(): void {
    if (this.coursesLoading || this.publishReadinessLoading || !!this.publishReadinessError) {
      return;
    }
    this.loadCourseSafePublishValidation();
  }

  retryQuickActions(): void {
    this.loadCourses();
    this.loadStudents();
  }

  retryTeacherSummary(): void {
    this.loadTeacherSummary();
  }

  retryRuntimeSupport(): void {
    if (this.coursesLoading) {
      return;
    }
    this.loadEducatorRuntimeSupport();
  }
}
