import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UserInfo } from '../../../models/user-info';
import { UsersService } from '../../../services/users.service';
import { CoursesService } from '../../../services/courses.service';
import { User } from '../../../models/user';
import { Course } from '../../../models/course';
import {
  CourseCompetencyEvidenceIntegrity,
  CourseGovernanceSummary,
  CoursePublishReadiness,
  CourseRuntimeInterventionRecommendation,
  CourseSafePublishValidation,
} from '../../../models/course-publish-readiness.model';
import { IconModule } from '../../../shared/icon/icon.module';
import { Router } from '@angular/router';
import { StatCardComponent } from '../../../components/stat-card/stat-card.component';
import { UsageStat, UsageStatsService } from '../../../services/usage-stats.service';
import { AnalyticsService } from '../../../services/analytics.service';
import { EchoStatePanelComponent } from '../../../components/echo-state-panel/echo-state-panel.component';
import { EchoLoadingStateComponent } from '../../../components/echo-loading-state/echo-loading-state.component';
import { forkJoin } from 'rxjs';

interface Metric {
  icon: string;
  label: string;
  value: number | string;
}

interface RuntimeInterventionCourseGroup {
  courseId: string;
  courseTitle: string;
  recommendations: CourseRuntimeInterventionRecommendation[];
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
  publishReadinessLoading = true;
  safePublishLoading = true;
  competencyIntegrityLoading = true;
  runtimeInterventionLoading = true;
  usersError = '';
  coursesError = '';
  usageStatsError = '';
  overviewError = '';
  publishReadinessError = '';
  safePublishError = '';
  competencyIntegrityError = '';
  runtimeInterventionError = '';
  courseReadiness: CoursePublishReadiness[] = [];
  safePublishValidations: CourseSafePublishValidation[] = [];
  competencyIntegrities: CourseCompetencyEvidenceIntegrity[] = [];
  runtimeInterventionRecommendations: CourseRuntimeInterventionRecommendation[] = [];
  courseGovernanceSummaries: CourseGovernanceSummary[] = [];

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
        this.loadCourseGovernanceSummary();
      },
      error: () => {
        this.courses = [];
        this.coursesLoading = false;
        this.coursesError = 'We could not load course management right now. Retry to restore the course catalog.';
        this.courseGovernanceSummaries = [];
        this.courseReadiness = [];
        this.publishReadinessLoading = false;
        this.publishReadinessError = '';
        this.safePublishValidations = [];
        this.safePublishLoading = false;
        this.safePublishError = '';
        this.competencyIntegrities = [];
        this.competencyIntegrityLoading = false;
        this.competencyIntegrityError = '';
        this.runtimeInterventionRecommendations = [];
        this.runtimeInterventionLoading = false;
        this.runtimeInterventionError = '';
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
        this.courseReadiness = this.courseReadiness.filter((readiness) => readiness.course_id !== courseId);
        this.safePublishValidations = this.safePublishValidations.filter((validation) => validation.course_id !== courseId);
        this.competencyIntegrities = this.competencyIntegrities.filter((integrity) => integrity.course_id !== courseId);
        this.runtimeInterventionRecommendations = this.runtimeInterventionRecommendations.filter((recommendation) => recommendation.course_id !== courseId);
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

  get publishReadinessSectionEmpty(): boolean {
    return !this.publishReadinessLoading && !this.publishReadinessError && this.courseReadiness.length === 0;
  }

  get safePublishSectionEmpty(): boolean {
    return !this.safePublishLoading && !this.safePublishError && this.safePublishValidations.length === 0;
  }

  get competencyIntegritySectionEmpty(): boolean {
    return !this.competencyIntegrityLoading && !this.competencyIntegrityError && this.competencyIntegrities.length === 0;
  }

  get runtimeInterventionSectionEmpty(): boolean {
    return !this.runtimeInterventionLoading && !this.runtimeInterventionError && this.runtimeInterventionRecommendations.length === 0;
  }

  get runtimeInterventionGroups(): RuntimeInterventionCourseGroup[] {
    const groups = new Map<string, RuntimeInterventionCourseGroup>();
    for (const recommendation of this.runtimeInterventionRecommendations) {
      if (!groups.has(recommendation.course_id)) {
        groups.set(recommendation.course_id, {
          courseId: recommendation.course_id,
          courseTitle: recommendation.course_title,
          recommendations: [],
        });
      }
      groups.get(recommendation.course_id)?.recommendations.push(recommendation);
    }

    return this.visibleCourses
      .map((course) => groups.get(course.id))
      .filter((group): group is RuntimeInterventionCourseGroup => !!group);
  }

  readinessStateLabel(isReady: boolean): string {
    return isReady ? 'Ready' : 'Not ready';
  }

  safePublishStateLabel(isSafe: boolean): string {
    return isSafe ? 'Safe' : 'Not safe';
  }

  competencyIntegrityStateLabel(isValid: boolean): string {
    return isValid ? 'Valid' : 'Not valid';
  }

  competencyExplainabilityLabel(isExplainable: boolean): string {
    return isExplainable ? 'Explainable' : 'Not explainable';
  }

  runtimeInterventionStateClasses(state: string): string {
    switch (state) {
      case 'enrichment':
        return 'bg-emerald-100 text-emerald-900 border border-emerald-200';
      case 'normal':
        return 'bg-slate-100 text-slate-800 border border-slate-200';
      case 'monitor':
        return 'bg-amber-100 text-amber-900 border border-amber-200';
      case 'review':
        return 'bg-sky-100 text-sky-900 border border-sky-200';
      case 'reteach':
        return 'bg-rose-100 text-rose-900 border border-rose-200';
      default:
        return 'bg-white text-slate-700 border border-slate-200';
    }
  }

  formatRuntimeLabel(value: string): string {
    return value
      .split(/[_-]/g)
      .filter((part) => part.length > 0)
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join(' ');
  }

  formatRuntimeLabels(values: string[]): string {
    return values.map((value) => this.formatRuntimeLabel(value)).join(', ');
  }

  loadCourseGovernanceSummary(): void {
    this.publishReadinessLoading = true;
    this.safePublishLoading = true;
    this.competencyIntegrityLoading = true;
    this.runtimeInterventionLoading = true;
    this.publishReadinessError = '';
    this.safePublishError = '';
    this.competencyIntegrityError = '';
    this.runtimeInterventionError = '';

    if (this.visibleCourses.length === 0) {
      this.courseGovernanceSummaries = [];
      this.courseReadiness = [];
      this.publishReadinessLoading = false;
      this.safePublishValidations = [];
      this.safePublishLoading = false;
      this.safePublishError = '';
      this.competencyIntegrities = [];
      this.competencyIntegrityLoading = false;
      this.competencyIntegrityError = '';
      this.runtimeInterventionRecommendations = [];
      this.runtimeInterventionLoading = false;
      this.runtimeInterventionError = '';
      return;
    }

    forkJoin(
      this.visibleCourses.map((course) => this.coursesService.getCourseGovernanceSummary(course.id)),
    ).subscribe({
      next: (summaries) => {
        this.courseGovernanceSummaries = summaries;
        this.courseReadiness = summaries.map((summary) => summary.publish_readiness);
        this.safePublishValidations = summaries.map((summary) => summary.safe_publish_validation);
        this.competencyIntegrities = summaries.map((summary) => summary.competency_evidence_integrity);
        this.runtimeInterventionRecommendations = summaries.reduce(
          (all, summary) => all.concat(summary.runtime_intervention_recommendations),
          [] as CourseRuntimeInterventionRecommendation[],
        );
        this.publishReadinessLoading = false;
        this.safePublishLoading = false;
        this.competencyIntegrityLoading = false;
        this.runtimeInterventionLoading = false;
      },
      error: () => {
        this.courseGovernanceSummaries = [];
        this.courseReadiness = [];
        this.publishReadinessLoading = false;
        this.publishReadinessError = 'We could not load course publish readiness right now. Retry to restore governance checks.';
        this.safePublishValidations = [];
        this.safePublishLoading = false;
        this.safePublishError = 'We could not load course safe-publish validation right now. Retry to restore learner-safety checks.';
        this.competencyIntegrities = [];
        this.competencyIntegrityLoading = false;
        this.competencyIntegrityError = 'We could not load competency evidence integrity right now. Retry to restore mastery explainability checks.';
        this.runtimeInterventionRecommendations = [];
        this.runtimeInterventionLoading = false;
        this.runtimeInterventionError = 'We could not load runtime intervention guidance right now. Retry to restore educator recommendation visibility.';
      },
    });
  }

  loadCourseSafePublishValidation(): void {
    this.loadCourseGovernanceSummary();
  }

  loadCourseCompetencyIntegrity(): void {
    this.loadCourseGovernanceSummary();
  }

  loadCourseRuntimeInterventions(): void {
    this.loadCourseGovernanceSummary();
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

  retryPublishReadiness(): void {
    if (this.coursesLoading) {
      return;
    }
    this.loadCourseGovernanceSummary();
  }

  retrySafePublish(): void {
    if (this.coursesLoading || this.publishReadinessLoading || !!this.publishReadinessError) {
      return;
    }
    this.loadCourseSafePublishValidation();
  }

  retryCompetencyIntegrity(): void {
    if (this.coursesLoading || this.publishReadinessLoading || !!this.publishReadinessError) {
      return;
    }
    this.loadCourseCompetencyIntegrity();
  }

  retryRuntimeInterventions(): void {
    if (this.coursesLoading || this.publishReadinessLoading || !!this.publishReadinessError) {
      return;
    }
    this.loadCourseRuntimeInterventions();
  }
}
