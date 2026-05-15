import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { of, Subject, throwError } from 'rxjs';

import { AdminViewComponent } from './admin-view.component';
import { UsersService } from '../../../services/users.service';
import { CoursesService } from '../../../services/courses.service';
import { UsageStatsService } from '../../../services/usage-stats.service';
import { AnalyticsService } from '../../../services/analytics.service';

class MockUsersService {
  usersResponse = of<any[]>([]);
  getUsers = jasmine.createSpy('getUsers').and.callFake(() => this.usersResponse);
  deleteUser = jasmine.createSpy('deleteUser').and.returnValue(of({}));
}

class MockCoursesService {
  coursesResponse = of<any[]>([]);
  getCourses = jasmine.createSpy('getCourses').and.callFake(() => this.coursesResponse);
  publishReadinessResponse = of<any>({
    course_id: 'course-1',
    course_title: 'Biology',
    is_ready: true,
    blocking_issue_count: 0,
    warning_count: 0,
    blocking_issues: [],
    warnings: [],
  });
  getCoursePublishReadiness = jasmine.createSpy('getCoursePublishReadiness').and.callFake(() => this.publishReadinessResponse);
  safePublishResponse = of<any>({
    course_id: 'course-1',
    course_title: 'Biology',
    is_safe: true,
    blocking_issue_count: 0,
    warning_count: 0,
    blocking_issues: [],
    warnings: [],
  });
  getCourseSafePublishValidation = jasmine.createSpy('getCourseSafePublishValidation').and.callFake(() => this.safePublishResponse);
  competencyIntegrityResponse = of<any>({
    course_id: 'course-1',
    course_title: 'Biology',
    is_valid: true,
    is_explainable: true,
    blocking_issue_count: 0,
    warning_count: 0,
    blocking_issues: [],
    warnings: [],
    affected_assessments: [],
    affected_competency_identifiers: [],
  });
  getCourseCompetencyEvidenceIntegrity = jasmine.createSpy('getCourseCompetencyEvidenceIntegrity').and.callFake(() => this.competencyIntegrityResponse);
  runtimeInterventionResponse = of<any[]>([]);
  getCourseRuntimeInterventionRecommendations = jasmine.createSpy('getCourseRuntimeInterventionRecommendations').and.callFake(() => this.runtimeInterventionResponse);
  deleteCourse = jasmine.createSpy('deleteCourse').and.returnValue(of({}));
}

class MockUsageStatsService {
  usageResponse = of<any[]>([]);
  getUsageStats = jasmine.createSpy('getUsageStats').and.callFake(() => this.usageResponse);
}

class MockAnalyticsService {
  overviewResponse = of({
    totals: {
      students: 0,
      teachers: 0,
      courses: 0,
      pending_enrollments: 0,
    },
  });
  getAdminOverview = jasmine.createSpy('getAdminOverview').and.callFake(() => this.overviewResponse);
}

describe('AdminViewComponent', () => {
  let component: AdminViewComponent;
  let fixture: ComponentFixture<AdminViewComponent>;
  let usersService: MockUsersService;
  let coursesService: MockCoursesService;
  let usageStatsService: MockUsageStatsService;
  let analyticsService: MockAnalyticsService;

  async function createComponent() {
    await TestBed.configureTestingModule({
      imports: [RouterTestingModule, HttpClientTestingModule, AdminViewComponent],
      providers: [
        { provide: UsersService, useClass: MockUsersService },
        { provide: CoursesService, useClass: MockCoursesService },
        { provide: UsageStatsService, useClass: MockUsageStatsService },
        { provide: AnalyticsService, useClass: MockAnalyticsService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AdminViewComponent);
    component = fixture.componentInstance;
    component.userInfo = { fullname: 'Admin Test', role: 'admin' } as any;
    usersService = TestBed.inject(UsersService) as unknown as MockUsersService;
    coursesService = TestBed.inject(CoursesService) as unknown as MockCoursesService;
    usageStatsService = TestBed.inject(UsageStatsService) as unknown as MockUsageStatsService;
    analyticsService = TestBed.inject(AnalyticsService) as unknown as MockAnalyticsService;
  }

  beforeEach(async () => {
    await createComponent();
  });

  it('uses EchoLoadingState while admin data is loading', () => {
    usersService.usersResponse = new Subject<any[]>().asObservable();
    coursesService.coursesResponse = new Subject<any[]>().asObservable();
    coursesService.publishReadinessResponse = new Subject<any>().asObservable();
    coursesService.safePublishResponse = new Subject<any>().asObservable();
    coursesService.competencyIntegrityResponse = new Subject<any>().asObservable();
    coursesService.runtimeInterventionResponse = new Subject<any[]>().asObservable();
    usageStatsService.usageResponse = new Subject<any[]>().asObservable();
    analyticsService.overviewResponse = new Subject<any>().asObservable();

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('[data-echo-loading="section"]')).not.toBeNull();
    expect(compiled.textContent).toContain('Loading platform overview');
    expect(compiled.textContent).toContain('Loading recent signups');
    expect(compiled.textContent).toContain('Loading publish readiness');
    expect(compiled.textContent).toContain('Loading safe publish validation');
    expect(compiled.textContent).toContain('Loading competency evidence integrity');
    expect(compiled.textContent).toContain('Loading runtime intervention recommendations');
  });

  it('uses EchoStatePanel for admin empty states', () => {
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const emptyStates = compiled.querySelectorAll('[data-echo-state="empty"]');
    expect(emptyStates.length).toBeGreaterThan(0);
    expect(compiled.textContent).toContain('Recent user activity will appear here');
    expect(compiled.textContent).toContain('Usage statistics will appear here');
    expect(compiled.textContent).toContain('Course management will appear here');
    expect(compiled.textContent).toContain('Publish readiness will appear here');
    expect(compiled.textContent).toContain('Safe publish validation will appear here');
    expect(compiled.textContent).toContain('Competency evidence integrity will appear here');
    expect(compiled.textContent).toContain('Runtime intervention recommendations will appear here');
  });

  it('uses EchoStatePanel for admin error states and retries data loads', () => {
    usersService.usersResponse = throwError(() => new Error('users failed'));
    coursesService.coursesResponse = throwError(() => new Error('courses failed'));
    usageStatsService.usageResponse = throwError(() => new Error('usage failed'));
    analyticsService.overviewResponse = throwError(() => new Error('overview failed'));

    fixture.detectChanges();
    expect(usersService.getUsers).toHaveBeenCalledTimes(1);
    expect(coursesService.getCourses).toHaveBeenCalledTimes(1);
    expect(usageStatsService.getUsageStats).toHaveBeenCalledTimes(1);
    expect(analyticsService.getAdminOverview).toHaveBeenCalledTimes(1);
    expect(coursesService.getCoursePublishReadiness).not.toHaveBeenCalled();

    usersService.usersResponse = of([{ id: 'user-1', firstname: 'Grace', lastname: 'Hopper', role: 'admin', created_at: '2026-05-01T00:00:00.000Z' }]);
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Biology' }]);
    coursesService.publishReadinessResponse = of({
      course_id: 'course-1',
      course_title: 'Biology',
      is_ready: true,
      blocking_issue_count: 0,
      warning_count: 0,
      blocking_issues: [],
      warnings: [],
    });
    coursesService.safePublishResponse = of({
      course_id: 'course-1',
      course_title: 'Biology',
      is_safe: true,
      blocking_issue_count: 0,
      warning_count: 0,
      blocking_issues: [],
      warnings: [],
    });
    coursesService.competencyIntegrityResponse = of({
      course_id: 'course-1',
      course_title: 'Biology',
      is_valid: true,
      is_explainable: true,
      blocking_issue_count: 0,
      warning_count: 0,
      blocking_issues: [],
      warnings: [],
      affected_assessments: [],
      affected_competency_identifiers: [],
    });
    coursesService.runtimeInterventionResponse = of([]);
    usageStatsService.usageResponse = of([{ label: 'Daily Active Users', value: 82, color: 'bg-primary' }]);
    analyticsService.overviewResponse = of({ totals: { students: 14, teachers: 2, courses: 5, pending_enrollments: 1 } });

    const buttons = Array.from(fixture.nativeElement.querySelectorAll('button')) as HTMLButtonElement[];
    buttons.filter((button) => button.textContent?.trim() === 'Retry').forEach((button) => button.click());
    fixture.detectChanges();

    expect(usersService.getUsers).toHaveBeenCalledTimes(2);
    expect(coursesService.getCourses).toHaveBeenCalledTimes(2);
    expect(usageStatsService.getUsageStats).toHaveBeenCalledTimes(2);
    expect(analyticsService.getAdminOverview).toHaveBeenCalledTimes(2);
    expect(coursesService.getCoursePublishReadiness).toHaveBeenCalled();
    expect(coursesService.getCourseSafePublishValidation).toHaveBeenCalled();
    expect(coursesService.getCourseCompetencyEvidenceIntegrity).toHaveBeenCalled();
    expect(coursesService.getCourseRuntimeInterventionRecommendations).toHaveBeenCalled();
  });

  it('keeps existing admin links and actions present', () => {
    usersService.usersResponse = of([{ id: 'user-1', firstname: 'Grace', lastname: 'Hopper', role: 'admin', created_at: '2026-05-01T00:00:00.000Z' }]);
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Biology' }]);
    usageStatsService.usageResponse = of([{ label: 'Daily Active Users', value: 82, color: 'bg-primary' }]);
    analyticsService.overviewResponse = of({ totals: { students: 14, teachers: 2, courses: 5, pending_enrollments: 1 } });

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Badge Management');
    expect(compiled.textContent).toContain('View All');
    expect(compiled.textContent).toContain('Course Management');
    expect(compiled.textContent).toContain('Delete');
    expect(compiled.textContent).not.toContain('Publish Course');
  });

  it('renders responsive fallback markup for educator data tables and cards', () => {
    usersService.usersResponse = of([{ id: 'user-1', firstname: 'Grace', lastname: 'Hopper', role: 'admin', created_at: '2026-05-01T00:00:00.000Z' }]);
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Biology' }]);
    usageStatsService.usageResponse = of([{ label: 'Daily Active Users', value: 82, color: 'bg-primary' }]);
    analyticsService.overviewResponse = of({ totals: { students: 14, teachers: 2, courses: 5, pending_enrollments: 1 } });

    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('[data-educator-responsive="admin-users"]')).not.toBeNull();
    expect(compiled.querySelector('[data-educator-responsive="admin-courses"]')).not.toBeNull();
  });

  it('renders publish readiness ready state for staff/admin surfaces', () => {
    usersService.usersResponse = of([{ id: 'user-1', firstname: 'Grace', lastname: 'Hopper', role: 'admin', created_at: '2026-05-01T00:00:00.000Z' }]);
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Biology' }]);
    coursesService.publishReadinessResponse = of({
      course_id: 'course-1',
      course_title: 'Biology',
      is_ready: true,
      blocking_issue_count: 0,
      warning_count: 1,
      blocking_issues: [],
      warnings: [{ entity_type: 'unit', entity_id: 'unit-1', entity_title: 'Unit One', code: 'empty_unit', message: 'Unit does not contain any lessons yet.' }],
    });
    usageStatsService.usageResponse = of([{ label: 'Daily Active Users', value: 82, color: 'bg-primary' }]);
    analyticsService.overviewResponse = of({ totals: { students: 14, teachers: 2, courses: 5, pending_enrollments: 1 } });

    fixture.detectChanges();

    expect(coursesService.getCoursePublishReadiness).toHaveBeenCalledWith('course-1');
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Publish readiness');
    expect(compiled.textContent).toContain('Biology');
    expect(compiled.textContent).toContain('Ready');
    expect(compiled.textContent).toContain('1 warning');
  });

  it('renders blocked publish readiness issues and retries read-only loading', () => {
    usersService.usersResponse = of([{ id: 'user-1', firstname: 'Grace', lastname: 'Hopper', role: 'admin', created_at: '2026-05-01T00:00:00.000Z' }]);
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Biology' }]);
    coursesService.publishReadinessResponse = throwError(() => new Error('publish readiness failed'));
    usageStatsService.usageResponse = of([{ label: 'Daily Active Users', value: 82, color: 'bg-primary' }]);
    analyticsService.overviewResponse = of({ totals: { students: 14, teachers: 2, courses: 5, pending_enrollments: 1 } });

    fixture.detectChanges();
    let compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('We could not load course publish readiness');

    coursesService.publishReadinessResponse = of({
      course_id: 'course-1',
      course_title: 'Biology',
      is_ready: false,
      blocking_issue_count: 2,
      warning_count: 0,
      blocking_issues: [
        { entity_type: 'lesson', entity_id: 'lesson-1', entity_title: 'Draft Lesson', code: 'review_status_not_approved', message: 'Lesson must be approved before it is publish-ready for learners.' },
        { entity_type: 'lesson', entity_id: 'lesson-1', entity_title: 'Draft Lesson', code: 'missing_readiness_field', message: 'Lesson is missing required publish-readiness field: sources.' },
      ],
      warnings: [],
    });

    const retryButton = Array.from(compiled.querySelectorAll('button')).find(
      (button) => button.textContent?.trim() === 'Retry',
    ) as HTMLButtonElement;
    retryButton.click();
    fixture.detectChanges();

    compiled = fixture.nativeElement as HTMLElement;
    expect(coursesService.getCoursePublishReadiness).toHaveBeenCalledTimes(2);
    expect(compiled.textContent).toContain('Not ready');
    expect(compiled.textContent).toContain('Draft Lesson');
    expect(compiled.textContent).toContain('sources');
    expect(coursesService.deleteCourse).not.toHaveBeenCalled();
  });

  it('renders safe-publish safe state for staff/admin surfaces', () => {
    usersService.usersResponse = of([{ id: 'user-1', firstname: 'Grace', lastname: 'Hopper', role: 'admin', created_at: '2026-05-01T00:00:00.000Z' }]);
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Biology' }]);
    coursesService.publishReadinessResponse = of({
      course_id: 'course-1',
      course_title: 'Biology',
      is_ready: true,
      blocking_issue_count: 0,
      warning_count: 0,
      blocking_issues: [],
      warnings: [],
    });
    coursesService.safePublishResponse = of({
      course_id: 'course-1',
      course_title: 'Biology',
      is_safe: true,
      blocking_issue_count: 0,
      warning_count: 1,
      blocking_issues: [],
      warnings: [
        { entity_type: 'course', entity_id: 'course-1', entity_title: 'Biology', code: 'draft_has_published_at', message: 'Draft revisions should not already have a published timestamp.' },
      ],
    });
    usageStatsService.usageResponse = of([{ label: 'Daily Active Users', value: 82, color: 'bg-primary' }]);
    analyticsService.overviewResponse = of({ totals: { students: 14, teachers: 2, courses: 5, pending_enrollments: 1 } });

    fixture.detectChanges();

    expect(coursesService.getCourseSafePublishValidation).toHaveBeenCalledWith('course-1');
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Safe publish validation');
    expect(compiled.textContent).toContain('Safe');
    expect(compiled.textContent).toContain('1 warning');
    expect(compiled.querySelector('[data-safe-publish-row]')).not.toBeNull();
  });

  it('renders competency integrity valid and explainable state for staff/admin surfaces', () => {
    usersService.usersResponse = of([{ id: 'user-1', firstname: 'Grace', lastname: 'Hopper', role: 'admin', created_at: '2026-05-01T00:00:00.000Z' }]);
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Biology' }]);
    coursesService.publishReadinessResponse = of({
      course_id: 'course-1',
      course_title: 'Biology',
      is_ready: true,
      blocking_issue_count: 0,
      warning_count: 0,
      blocking_issues: [],
      warnings: [],
    });
    coursesService.safePublishResponse = of({
      course_id: 'course-1',
      course_title: 'Biology',
      is_safe: true,
      blocking_issue_count: 0,
      warning_count: 0,
      blocking_issues: [],
      warnings: [],
    });
    coursesService.competencyIntegrityResponse = of({
      course_id: 'course-1',
      course_title: 'Biology',
      is_valid: true,
      is_explainable: true,
      blocking_issue_count: 0,
      warning_count: 1,
      blocking_issues: [],
      warnings: [
        { entity_type: 'assessment', entity_id: 'assessment-2', entity_title: 'Practice Quiz', code: 'unaligned_assessment_mastery_evidence', message: 'Assessment evidence is not aligned to a competency.' },
      ],
      affected_assessments: [],
      affected_competency_identifiers: [],
    });
    usageStatsService.usageResponse = of([{ label: 'Daily Active Users', value: 82, color: 'bg-primary' }]);
    analyticsService.overviewResponse = of({ totals: { students: 14, teachers: 2, courses: 5, pending_enrollments: 1 } });

    fixture.detectChanges();

    expect(coursesService.getCourseCompetencyEvidenceIntegrity).toHaveBeenCalledWith('course-1');
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Competency evidence integrity');
    expect(compiled.textContent).toContain('Valid');
    expect(compiled.textContent).toContain('Explainable');
    expect(compiled.textContent).toContain('1 warning');
    expect(compiled.querySelector('[data-competency-integrity-row]')).not.toBeNull();
  });

  it('renders competency integrity affected assessments, competencies, and issues with retry and no mutation actions', () => {
    usersService.usersResponse = of([{ id: 'user-1', firstname: 'Grace', lastname: 'Hopper', role: 'admin', created_at: '2026-05-01T00:00:00.000Z' }]);
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Biology' }]);
    coursesService.publishReadinessResponse = of({
      course_id: 'course-1',
      course_title: 'Biology',
      is_ready: true,
      blocking_issue_count: 0,
      warning_count: 0,
      blocking_issues: [],
      warnings: [],
    });
    coursesService.safePublishResponse = of({
      course_id: 'course-1',
      course_title: 'Biology',
      is_safe: true,
      blocking_issue_count: 0,
      warning_count: 0,
      blocking_issues: [],
      warnings: [],
    });
    coursesService.competencyIntegrityResponse = throwError(() => new Error('integrity failed'));
    usageStatsService.usageResponse = of([{ label: 'Daily Active Users', value: 82, color: 'bg-primary' }]);
    analyticsService.overviewResponse = of({ totals: { students: 14, teachers: 2, courses: 5, pending_enrollments: 1 } });

    fixture.detectChanges();
    let compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('We could not load competency evidence integrity');

    coursesService.competencyIntegrityResponse = of({
      course_id: 'course-1',
      course_title: 'Biology',
      is_valid: false,
      is_explainable: false,
      blocking_issue_count: 1,
      warning_count: 1,
      blocking_issues: [
        { entity_type: 'assessment', entity_id: 'assessment-1', entity_title: 'Final Assessment', code: 'missing_attempt_event_for_mastery_evidence', message: 'Attempt evidence is missing an authoritative event.' },
      ],
      warnings: [
        { entity_type: 'assessment', entity_id: 'assessment-2', entity_title: 'Practice Quiz', code: 'unaligned_assessment_mastery_evidence', message: 'Assessment evidence is not aligned to a competency.' },
      ],
      affected_assessments: [
        { assessment_id: 'assessment-1', assessment_title: 'Final Assessment', competency_identifiers: ['evidence', 'analysis'] },
        { assessment_id: 'assessment-2', assessment_title: 'Practice Quiz', competency_identifiers: [] },
      ],
      affected_competency_identifiers: ['evidence', 'analysis'],
    });

    const retryButtons = Array.from(compiled.querySelectorAll('button')).filter(
      (button) => button.textContent?.trim() === 'Retry',
    ) as HTMLButtonElement[];
    retryButtons[0]?.click();
    fixture.detectChanges();

    compiled = fixture.nativeElement as HTMLElement;
    expect(coursesService.getCourseCompetencyEvidenceIntegrity).toHaveBeenCalledTimes(2);
    expect(compiled.textContent).toContain('Not valid');
    expect(compiled.textContent).toContain('Not explainable');
    expect(compiled.textContent).toContain('Affected competencies');
    expect(compiled.textContent).toContain('evidence, analysis');
    expect(compiled.textContent).toContain('Final Assessment');
    expect(compiled.textContent).toContain('Practice Quiz');
    expect(compiled.textContent).toContain('Attempt evidence is missing an authoritative event.');
    expect(coursesService.deleteCourse).not.toHaveBeenCalled();
  });

  it('renders runtime intervention recommendation states, evidence basis, and caution flags for admin staff', () => {
    usersService.usersResponse = of([{ id: 'user-1', firstname: 'Grace', lastname: 'Hopper', role: 'admin', created_at: '2026-05-01T00:00:00.000Z' }]);
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Biology' }]);
    coursesService.publishReadinessResponse = of({
      course_id: 'course-1',
      course_title: 'Biology',
      is_ready: true,
      blocking_issue_count: 0,
      warning_count: 0,
      blocking_issues: [],
      warnings: [],
    });
    coursesService.safePublishResponse = of({
      course_id: 'course-1',
      course_title: 'Biology',
      is_safe: true,
      blocking_issue_count: 0,
      warning_count: 0,
      blocking_issues: [],
      warnings: [],
    });
    coursesService.competencyIntegrityResponse = of({
      course_id: 'course-1',
      course_title: 'Biology',
      is_valid: true,
      is_explainable: true,
      blocking_issue_count: 0,
      warning_count: 0,
      blocking_issues: [],
      warnings: [],
      affected_assessments: [],
      affected_competency_identifiers: [],
    });
    coursesService.runtimeInterventionResponse = of([
      {
        student_id: 'student-1',
        student_name: 'Ada Lovelace',
        student_course_id: 'student-course-1',
        course_id: 'course-1',
        course_title: 'Biology',
        recommendation_state: 'review',
        educator_attention_level: 'medium',
        summary: 'Recent evidence suggests a brief review conversation may help.',
        evidence_basis: [
          {
            source: 'mastery_summary',
            detail: 'Mastery evidence is mixed but explainable.',
            assessment_id: 'assessment-1',
            assessment_title: 'Practice Quiz',
            competency_identifiers: ['evidence'],
          },
        ],
        confidence_level: 'moderate',
        caution_flags: ['ambiguous_evidence'],
        learner_safe_message: 'Offer calm review support and preserve the learner’s confidence.',
      },
    ]);
    usageStatsService.usageResponse = of([{ label: 'Daily Active Users', value: 82, color: 'bg-primary' }]);
    analyticsService.overviewResponse = of({ totals: { students: 14, teachers: 2, courses: 5, pending_enrollments: 1 } });

    fixture.detectChanges();

    expect(coursesService.getCourseRuntimeInterventionRecommendations).toHaveBeenCalledWith('course-1');
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Runtime intervention recommendations');
    expect(compiled.textContent).toContain('Ada Lovelace');
    expect(compiled.textContent).toContain('Review');
    expect(compiled.textContent).toContain('Medium attention');
    expect(compiled.textContent).toContain('Evidence basis');
    expect(compiled.textContent).toContain('Mastery Summary');
    expect(compiled.textContent).toContain('Practice Quiz');
    expect(compiled.textContent).toContain('Caution flags');
    expect(compiled.textContent).toContain('Ambiguous Evidence');
    expect(compiled.querySelector('[data-runtime-intervention-row]')).not.toBeNull();
    const runtimeButtons = compiled.querySelectorAll('[data-runtime-intervention-row] button');
    expect(runtimeButtons.length).toBe(0);
  });

  it('renders runtime intervention error state and retries read-only loading for admin staff', () => {
    usersService.usersResponse = of([{ id: 'user-1', firstname: 'Grace', lastname: 'Hopper', role: 'admin', created_at: '2026-05-01T00:00:00.000Z' }]);
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Biology' }]);
    coursesService.publishReadinessResponse = of({
      course_id: 'course-1',
      course_title: 'Biology',
      is_ready: true,
      blocking_issue_count: 0,
      warning_count: 0,
      blocking_issues: [],
      warnings: [],
    });
    coursesService.safePublishResponse = of({
      course_id: 'course-1',
      course_title: 'Biology',
      is_safe: true,
      blocking_issue_count: 0,
      warning_count: 0,
      blocking_issues: [],
      warnings: [],
    });
    coursesService.competencyIntegrityResponse = of({
      course_id: 'course-1',
      course_title: 'Biology',
      is_valid: true,
      is_explainable: true,
      blocking_issue_count: 0,
      warning_count: 0,
      blocking_issues: [],
      warnings: [],
      affected_assessments: [],
      affected_competency_identifiers: [],
    });
    coursesService.runtimeInterventionResponse = throwError(() => new Error('runtime intervention failed'));
    usageStatsService.usageResponse = of([{ label: 'Daily Active Users', value: 82, color: 'bg-primary' }]);
    analyticsService.overviewResponse = of({ totals: { students: 14, teachers: 2, courses: 5, pending_enrollments: 1 } });

    fixture.detectChanges();
    let compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('We could not load runtime intervention recommendations');

    coursesService.runtimeInterventionResponse = of([]);
    const retryButtons = Array.from(compiled.querySelectorAll('button')).filter(
      (button) => button.textContent?.trim() === 'Retry',
    ) as HTMLButtonElement[];
    retryButtons[0]?.click();
    fixture.detectChanges();

    compiled = fixture.nativeElement as HTMLElement;
    expect(coursesService.getCourseRuntimeInterventionRecommendations).toHaveBeenCalledTimes(2);
    expect(coursesService.deleteCourse).not.toHaveBeenCalled();
    expect(compiled.textContent).toContain('Runtime intervention recommendations will appear here');
  });

  it('renders blocked safe-publish issues and retries read-only loading', () => {
    usersService.usersResponse = of([{ id: 'user-1', firstname: 'Grace', lastname: 'Hopper', role: 'admin', created_at: '2026-05-01T00:00:00.000Z' }]);
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Biology' }]);
    coursesService.publishReadinessResponse = of({
      course_id: 'course-1',
      course_title: 'Biology',
      is_ready: true,
      blocking_issue_count: 0,
      warning_count: 0,
      blocking_issues: [],
      warnings: [],
    });
    coursesService.safePublishResponse = throwError(() => new Error('safe publish failed'));
    usageStatsService.usageResponse = of([{ label: 'Daily Active Users', value: 82, color: 'bg-primary' }]);
    analyticsService.overviewResponse = of({ totals: { students: 14, teachers: 2, courses: 5, pending_enrollments: 1 } });

    fixture.detectChanges();
    let compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('We could not load course safe-publish validation');

    coursesService.safePublishResponse = of({
      course_id: 'course-1',
      course_title: 'Biology',
      is_safe: false,
      blocking_issue_count: 1,
      warning_count: 1,
      blocking_issues: [
        { entity_type: 'course', entity_id: 'course-1', entity_title: 'Biology', code: 'blocked_revision_status', message: 'Deprecated or archived content is not safe to republish for learners.' },
      ],
      warnings: [
        { entity_type: 'course', entity_id: 'course-1', entity_title: 'Biology', code: 'draft_has_published_at', message: 'Draft revisions should not already have a published timestamp.' },
      ],
    });

    const retryButtons = Array.from(compiled.querySelectorAll('button')).filter(
      (button) => button.textContent?.trim() === 'Retry',
    ) as HTMLButtonElement[];
    retryButtons[0]?.click();
    fixture.detectChanges();

    compiled = fixture.nativeElement as HTMLElement;
    expect(coursesService.getCourseSafePublishValidation).toHaveBeenCalledTimes(2);
    expect(compiled.textContent).toContain('Not safe');
    expect(compiled.textContent).toContain('Deprecated or archived content is not safe to republish for learners.');
    expect(coursesService.deleteCourse).not.toHaveBeenCalled();
  });
});
