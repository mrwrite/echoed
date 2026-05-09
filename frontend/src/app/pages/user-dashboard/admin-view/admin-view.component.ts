import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UserInfo } from '../../../models/user-info';
import { UsersService } from '../../../services/users.service';
import { CoursesService } from '../../../services/courses.service';
import { User } from '../../../models/user';
import { Course } from '../../../models/course';
import { IconModule } from '../../../shared/icon/icon.module';
import { Router } from '@angular/router';
import { StatCardComponent } from '../../../components/stat-card/stat-card.component';
import { UsageStat, UsageStatsService } from '../../../services/usage-stats.service';
import { AnalyticsService } from '../../../services/analytics.service';
import { EchoStatePanelComponent } from '../../../components/echo-state-panel/echo-state-panel.component';
import { EchoLoadingStateComponent } from '../../../components/echo-loading-state/echo-loading-state.component';

interface Metric {
  icon: string;
  label: string;
  value: number | string;
}

@Component({
  selector: 'echoed-admin-view',
  standalone: true,
  imports: [CommonModule, IconModule, StatCardComponent, EchoStatePanelComponent, EchoLoadingStateComponent],
  templateUrl: './admin-view.component.html',
  styleUrl: './admin-view.component.scss'
})
export class AdminViewComponent {
  @Input() userInfo!: UserInfo;
  users: User[] = [];
  courses: Course[] = [];
  usageStats: UsageStat[] = [];

  /** Number of items visible in dashboard */
  readonly visibleCount = 5;

  studentCount = 0;
  teacherCount = 0;
  coursesCount = 0;
  pendingEnrollments = 0;
  metrics: Metric[] = [];
  usersLoading = true;
  coursesLoading = true;
  usageStatsLoading = true;
  overviewLoading = true;
  usersError = '';
  coursesError = '';
  usageStatsError = '';
  overviewError = '';

  constructor(
    private usersService: UsersService,
    private coursesService: CoursesService,
    private router: Router,
    private usageStatsService: UsageStatsService,
    private analyticsService: AnalyticsService
  ) {}

  ngOnInit() {
    this.loadUsers();
    this.loadCourses();
    this.loadOverview();
    this.loadUsageStats();
  }

  loadUsers(): void {
    this.usersLoading = true;
    this.usersError = '';
    this.usersService.getUsers().subscribe({
      next: (users: User[]) => {
        this.users = users;
        this.usersLoading = false;
      },
      error: () => {
        this.users = [];
        this.usersLoading = false;
        this.usersError = 'We could not load recent user activity right now. Retry to restore signups.';
      },
    });
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
        this.coursesError = 'We could not load course management right now. Retry to restore the course catalog.';
      },
    });
  }

  loadOverview(): void {
    this.overviewLoading = true;
    this.overviewError = '';
    this.analyticsService.getAdminOverview().subscribe({
      next: (overview) => {
        this.studentCount = overview.totals.students;
        this.teacherCount = overview.totals.teachers;
        this.coursesCount = overview.totals.courses;
        this.pendingEnrollments = overview.totals.pending_enrollments;
        this.updateMetrics();
        this.overviewLoading = false;
      },
      error: () => {
        this.metrics = [];
        this.overviewLoading = false;
        this.overviewError = 'We could not load the platform overview right now. Retry to restore admin metrics.';
      },
    });
  }

  loadUsageStats(): void {
    this.usageStatsLoading = true;
    this.usageStatsError = '';
    this.usageStatsService.getUsageStats().subscribe({
      next: (stats) => {
        this.usageStats = stats;
        this.usageStatsLoading = false;
      },
      error: () => {
        this.usageStats = [];
        this.usageStatsLoading = false;
        this.usageStatsError = 'We could not load usage statistics right now. Retry to restore platform activity insights.';
      },
    });
  }

  private updateMetrics() {
    this.metrics = [
      { icon: 'User', label: 'Active Students', value: this.studentCount },
      { icon: 'User', label: 'Instructors', value: this.teacherCount },
      { icon: 'book-marked', label: 'Courses', value: this.coursesCount },
      { icon: 'clock', label: 'Pending Enrollments', value: this.pendingEnrollments }
    ];
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
        this.coursesCount = this.courses.length;
        this.updateMetrics();
      },
    });
  }

  /** Users displayed on dashboard */
  get visibleUsers(): User[] {
    return this.users.slice(0, this.visibleCount);
  }

  deleteUser(userId: string) {
    this.usersService.deleteUser(userId).subscribe({
      next: () => {
        this.users = this.users.filter(u => u.id !== userId);
        this.studentCount = this.users.filter(u => u.role === 'student').length;
        this.teacherCount = this.users.filter(u => u.role === 'teacher').length;
        this.updateMetrics();
      },
    });
  }

  /** Courses displayed on dashboard */
  get visibleCourses(): Course[] {
    return this.courses.slice(0, this.visibleCount);
  }

  viewAllUsers() {
    this.router.navigate(['/home/admin/users']);
  }

  viewAllCourses() {
    this.router.navigate(['/home/admin/courses']);
  }

  viewAllBadges() {
    this.router.navigate(['/home/admin/badges']);
  }

  retryOverview(): void {
    this.loadOverview();
  }

  retryUsers(): void {
    this.loadUsers();
  }

  retryUsageStats(): void {
    this.loadUsageStats();
  }

  retryCourses(): void {
    this.loadCourses();
  }
}
