import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { UserInfo } from '../../../models/user-info';
import { CoursesService } from '../../../services/courses.service';
import { Course } from '../../../models/course';
import { IconModule } from '../../../shared/icon/icon.module';
import { ToastService } from '../../../services/toast.service';
import { AnalyticsService, TeacherSummaryRow } from '../../../services/analytics.service';
import { UsersService } from '../../../services/users.service';
import { User } from '../../../models/user';
import { EchoStatePanelComponent } from '../../../components/echo-state-panel/echo-state-panel.component';
import { EchoLoadingStateComponent } from '../../../components/echo-loading-state/echo-loading-state.component';

@Component({
  selector: 'echoed-teacher-view',
  standalone: true,
  imports: [CommonModule, FormsModule, IconModule, EchoStatePanelComponent, EchoLoadingStateComponent],
  templateUrl: './teacher-view.component.html',
  styleUrl: './teacher-view.component.scss'
})
export class TeacherViewComponent implements OnInit {
  @Input() userInfo!: UserInfo;

  courses: Course[] = [];
  readonly visibleCount = 5;
  students: User[] = [];
  teacherSummary: TeacherSummaryRow[] = [];
  selectedCourseId = '';
  selectedStudentId = '';
  coursesLoading = true;
  studentsLoading = true;
  summaryLoading = true;
  coursesError = '';
  studentsError = '';
  summaryError = '';

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

  loadCourses(): void {
    this.coursesLoading = true;
    this.coursesError = '';
    this.coursesService.getCourses().subscribe({
      next: (courses) => {
        this.courses = courses;
        this.coursesLoading = false;
      },
      error: () => {
        this.courses = [];
        this.coursesLoading = false;
        this.coursesError = 'We could not load educator courses right now. Retry to restore course management.';
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

  retryQuickActions(): void {
    this.loadCourses();
    this.loadStudents();
  }

  retryTeacherSummary(): void {
    this.loadTeacherSummary();
  }
}
