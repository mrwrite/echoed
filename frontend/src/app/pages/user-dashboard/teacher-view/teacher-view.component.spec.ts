import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { of, Subject, throwError } from 'rxjs';

import { TeacherViewComponent } from './teacher-view.component';
import { CoursesService } from '../../../services/courses.service';
import { AnalyticsService } from '../../../services/analytics.service';
import { UsersService } from '../../../services/users.service';
import { ToastService } from '../../../services/toast.service';

class MockCoursesService {
  coursesResponse = of<any[]>([]);
  getCourses = jasmine.createSpy('getCourses').and.callFake(() => this.coursesResponse);
  publishReadinessResponse = of<any>({
    course_id: 'course-1',
    course_title: 'Introduction to Africa',
    is_ready: true,
    blocking_issue_count: 0,
    warning_count: 0,
    blocking_issues: [],
    warnings: [],
  });
  getCoursePublishReadiness = jasmine.createSpy('getCoursePublishReadiness').and.callFake(() => this.publishReadinessResponse);
  safePublishResponse = of<any>({
    course_id: 'course-1',
    course_title: 'Introduction to Africa',
    is_safe: true,
    blocking_issue_count: 0,
    warning_count: 0,
    blocking_issues: [],
    warnings: [],
  });
  getCourseSafePublishValidation = jasmine.createSpy('getCourseSafePublishValidation').and.callFake(() => this.safePublishResponse);
  deleteCourse = jasmine.createSpy('deleteCourse').and.returnValue(of({}));
  assignCourseToStudent = jasmine.createSpy('assignCourseToStudent').and.returnValue(of({}));
}

class MockAnalyticsService {
  summaryResponse = of<any[]>([]);
  runtimeSupportResponse = of<any[]>([]);
  getTeacherSummary = jasmine.createSpy('getTeacherSummary').and.callFake(() => this.summaryResponse);
  getEducatorRuntimeSupport = jasmine.createSpy('getEducatorRuntimeSupport').and.callFake(() => this.runtimeSupportResponse);
}

class MockUsersService {
  studentsResponse = of<any[]>([]);
  getStudents = jasmine.createSpy('getStudents').and.callFake(() => this.studentsResponse);
}

class MockToastService {
  show = jasmine.createSpy('show');
}

describe('TeacherViewComponent', () => {
  let component: TeacherViewComponent;
  let fixture: ComponentFixture<TeacherViewComponent>;
  let coursesService: MockCoursesService;
  let analyticsService: MockAnalyticsService;
  let usersService: MockUsersService;
  let router: Router;

  async function createComponent() {
    await TestBed.configureTestingModule({
      imports: [RouterTestingModule, HttpClientTestingModule, TeacherViewComponent],
      providers: [
        { provide: CoursesService, useClass: MockCoursesService },
        { provide: AnalyticsService, useClass: MockAnalyticsService },
        { provide: UsersService, useClass: MockUsersService },
        { provide: ToastService, useClass: MockToastService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(TeacherViewComponent);
    component = fixture.componentInstance;
    component.userInfo = { fullname: 'Teacher Test', role: 'teacher' } as any;
    coursesService = TestBed.inject(CoursesService) as unknown as MockCoursesService;
    analyticsService = TestBed.inject(AnalyticsService) as unknown as MockAnalyticsService;
    usersService = TestBed.inject(UsersService) as unknown as MockUsersService;
    router = TestBed.inject(Router);
  }

  beforeEach(async () => {
    await createComponent();
  });

  it('uses EchoLoadingState while teacher data is loading', () => {
    const pendingCourses = new Subject<any[]>();
    const pendingStudents = new Subject<any[]>();
    const pendingSummary = new Subject<any[]>();
    const pendingRuntimeSupport = new Subject<any[]>();
    const pendingPublishReadiness = new Subject<any>();
    const pendingSafePublish = new Subject<any>();
    coursesService.coursesResponse = pendingCourses.asObservable();
    coursesService.publishReadinessResponse = pendingPublishReadiness.asObservable();
    coursesService.safePublishResponse = pendingSafePublish.asObservable();
    usersService.studentsResponse = pendingStudents.asObservable();
    analyticsService.summaryResponse = pendingSummary.asObservable();
    analyticsService.runtimeSupportResponse = pendingRuntimeSupport.asObservable();

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('[data-echo-loading="section"]')).not.toBeNull();
    expect(compiled.textContent).toContain('Loading course management');
    expect(compiled.textContent).toContain('Loading student progress');
    expect(compiled.textContent).toContain('Loading runtime support');
    expect(compiled.textContent).toContain('Loading publish readiness');
    expect(compiled.textContent).toContain('Loading safe publish validation');
  });

  it('uses EchoStatePanel for teacher empty states', () => {
    coursesService.coursesResponse = of([]);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const emptyStates = compiled.querySelectorAll('[data-echo-state="empty"]');
    expect(emptyStates.length).toBeGreaterThan(0);
    expect(compiled.textContent).toContain('Course management will appear here');
    expect(compiled.textContent).toContain('Student progress will appear here');
    expect(compiled.textContent).toContain('Flagship runtime support is not available yet');
    expect(compiled.textContent).toContain('Publish readiness will appear here');
    expect(compiled.textContent).toContain('Safe publish validation will appear here');
  });

  it('uses EchoStatePanel for teacher error states and retries data loads', () => {
    coursesService.coursesResponse = throwError(() => new Error('courses failed'));
    usersService.studentsResponse = throwError(() => new Error('students failed'));
    analyticsService.summaryResponse = throwError(() => new Error('summary failed'));
    analyticsService.runtimeSupportResponse = throwError(() => new Error('runtime support failed'));

    fixture.detectChanges();
    expect(coursesService.getCourses).toHaveBeenCalledTimes(1);
    expect(usersService.getStudents).toHaveBeenCalledTimes(1);
    expect(analyticsService.getTeacherSummary).toHaveBeenCalledTimes(1);
    expect(analyticsService.getEducatorRuntimeSupport).not.toHaveBeenCalled();
    expect(coursesService.getCoursePublishReadiness).not.toHaveBeenCalled();

    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Introduction to Africa', standards_metadata: { pathway_key: 'introduction-to-africa' } }]);
    coursesService.publishReadinessResponse = of({
      course_id: 'course-1',
      course_title: 'Introduction to Africa',
      is_ready: true,
      blocking_issue_count: 0,
      warning_count: 0,
      blocking_issues: [],
      warnings: [],
    });
    coursesService.safePublishResponse = of({
      course_id: 'course-1',
      course_title: 'Introduction to Africa',
      is_safe: true,
      blocking_issue_count: 0,
      warning_count: 0,
      blocking_issues: [],
      warnings: [],
    });
    usersService.studentsResponse = of([{ id: 'student-1', firstname: 'Ada', lastname: 'Lovelace' }]);
    analyticsService.summaryResponse = of([{ student_name: 'Ada Lovelace', course_title: 'Algebra I', progress: 50, status: 'active', last_active: '2026-05-01T00:00:00.000Z' }]);
    analyticsService.runtimeSupportResponse = of([]);

    const buttons = Array.from(fixture.nativeElement.querySelectorAll('button')) as HTMLButtonElement[];
    const retryLabels = ['Retry'];
    buttons.filter((button) => retryLabels.includes(button.textContent?.trim() || '')).forEach((button) => button.click());
    fixture.detectChanges();

    expect(coursesService.getCourses).toHaveBeenCalledTimes(3);
    expect(usersService.getStudents).toHaveBeenCalledTimes(2);
    expect(analyticsService.getTeacherSummary).toHaveBeenCalledTimes(2);
    expect(analyticsService.getEducatorRuntimeSupport).toHaveBeenCalledTimes(2);
    expect(coursesService.getCoursePublishReadiness).toHaveBeenCalled();
    expect(coursesService.getCourseSafePublishValidation).toHaveBeenCalled();
  });

  it('keeps existing teacher actions and links present', () => {
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Introduction to Africa', standards_metadata: { pathway_key: 'introduction-to-africa' } }]);
    usersService.studentsResponse = of([{ id: 'student-1', firstname: 'Ada', lastname: 'Lovelace' }]);
    analyticsService.summaryResponse = of([{ student_name: 'Ada Lovelace', course_title: 'Algebra I', progress: 50, status: 'active', last_active: '2026-05-01T00:00:00.000Z' }]);
    analyticsService.runtimeSupportResponse = of([]);

    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Add Course');
    expect(compiled.textContent).toContain('Assign Course');
    expect(compiled.textContent).toContain('Start Live Lesson');
    expect(compiled.textContent).toContain('View Reports');
    expect(compiled.textContent).not.toContain('Publish Course');
  });

  it('renders responsive fallback markup for educator tables', () => {
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Introduction to Africa', standards_metadata: { pathway_key: 'introduction-to-africa' } }]);
    usersService.studentsResponse = of([{ id: 'student-1', firstname: 'Ada', lastname: 'Lovelace' }]);
    analyticsService.summaryResponse = of([{ student_name: 'Ada Lovelace', course_title: 'Algebra I', progress: 50, status: 'active', last_active: '2026-05-01T00:00:00.000Z' }]);
    analyticsService.runtimeSupportResponse = of([]);

    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('[data-educator-responsive="teacher-courses"]')).not.toBeNull();
    expect(compiled.querySelector('[data-educator-responsive="teacher-summary"]')).not.toBeNull();
  });

  it('renders publish readiness ready state in the teacher staff surface', () => {
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Introduction to Africa', standards_metadata: { pathway_key: 'introduction-to-africa' } }]);
    coursesService.publishReadinessResponse = of({
      course_id: 'course-1',
      course_title: 'Introduction to Africa',
      is_ready: true,
      blocking_issue_count: 0,
      warning_count: 1,
      blocking_issues: [],
      warnings: [{ entity_type: 'unit', entity_id: 'unit-1', entity_title: 'Unit One', code: 'empty_unit', message: 'Unit does not contain any lessons yet.' }],
    });
    usersService.studentsResponse = of([{ id: 'student-1', firstname: 'Ada', lastname: 'Lovelace' }]);
    analyticsService.summaryResponse = of([]);
    analyticsService.runtimeSupportResponse = of([]);

    fixture.detectChanges();

    expect(coursesService.getCoursePublishReadiness).toHaveBeenCalledWith('course-1');
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Publish readiness');
    expect(compiled.textContent).toContain('Introduction to Africa');
    expect(compiled.textContent).toContain('Ready');
    expect(compiled.textContent).toContain('1 warning');
  });

  it('renders blocked publish readiness issues with retry and no mutation actions', () => {
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Introduction to Africa', standards_metadata: { pathway_key: 'introduction-to-africa' } }]);
    coursesService.publishReadinessResponse = throwError(() => new Error('readiness failed'));
    usersService.studentsResponse = of([{ id: 'student-1', firstname: 'Ada', lastname: 'Lovelace' }]);
    analyticsService.summaryResponse = of([]);
    analyticsService.runtimeSupportResponse = of([]);

    fixture.detectChanges();
    let compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('We could not load course publish readiness');

    coursesService.publishReadinessResponse = of({
      course_id: 'course-1',
      course_title: 'Introduction to Africa',
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
    expect(coursesService.assignCourseToStudent).not.toHaveBeenCalled();
    expect(coursesService.deleteCourse).not.toHaveBeenCalled();
  });

  it('renders safe-publish safe state in the teacher staff surface', () => {
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Introduction to Africa', standards_metadata: { pathway_key: 'introduction-to-africa' } }]);
    coursesService.publishReadinessResponse = of({
      course_id: 'course-1',
      course_title: 'Introduction to Africa',
      is_ready: true,
      blocking_issue_count: 0,
      warning_count: 0,
      blocking_issues: [],
      warnings: [],
    });
    coursesService.safePublishResponse = of({
      course_id: 'course-1',
      course_title: 'Introduction to Africa',
      is_safe: true,
      blocking_issue_count: 0,
      warning_count: 1,
      blocking_issues: [],
      warnings: [
        { entity_type: 'course', entity_id: 'course-1', entity_title: 'Introduction to Africa', code: 'draft_has_published_at', message: 'Draft revisions should not already have a published timestamp.' },
      ],
    });
    usersService.studentsResponse = of([{ id: 'student-1', firstname: 'Ada', lastname: 'Lovelace' }]);
    analyticsService.summaryResponse = of([]);
    analyticsService.runtimeSupportResponse = of([]);

    fixture.detectChanges();

    expect(coursesService.getCourseSafePublishValidation).toHaveBeenCalledWith('course-1');
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Safe publish validation');
    expect(compiled.textContent).toContain('Safe');
    expect(compiled.textContent).toContain('1 warning');
    expect(compiled.querySelector('[data-safe-publish-row]')).not.toBeNull();
  });

  it('renders blocked safe-publish issues with retry and no mutation actions', () => {
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Introduction to Africa', standards_metadata: { pathway_key: 'introduction-to-africa' } }]);
    coursesService.publishReadinessResponse = of({
      course_id: 'course-1',
      course_title: 'Introduction to Africa',
      is_ready: true,
      blocking_issue_count: 0,
      warning_count: 0,
      blocking_issues: [],
      warnings: [],
    });
    coursesService.safePublishResponse = throwError(() => new Error('safe publish failed'));
    usersService.studentsResponse = of([{ id: 'student-1', firstname: 'Ada', lastname: 'Lovelace' }]);
    analyticsService.summaryResponse = of([]);
    analyticsService.runtimeSupportResponse = of([]);

    fixture.detectChanges();
    let compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('We could not load course safe-publish validation');

    coursesService.safePublishResponse = of({
      course_id: 'course-1',
      course_title: 'Introduction to Africa',
      is_safe: false,
      blocking_issue_count: 1,
      warning_count: 1,
      blocking_issues: [
        { entity_type: 'course', entity_id: 'course-1', entity_title: 'Introduction to Africa', code: 'blocked_revision_status', message: 'Deprecated or archived content is not safe to republish for learners.' },
      ],
      warnings: [
        { entity_type: 'course', entity_id: 'course-1', entity_title: 'Introduction to Africa', code: 'draft_has_published_at', message: 'Draft revisions should not already have a published timestamp.' },
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
    expect(coursesService.assignCourseToStudent).not.toHaveBeenCalled();
    expect(coursesService.deleteCourse).not.toHaveBeenCalled();
  });

  it('loads runtime support for the flagship course and renders remediation context', () => {
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Introduction to Africa', standards_metadata: { pathway_key: 'introduction-to-africa' } }]);
    usersService.studentsResponse = of([{ id: 'student-1', firstname: 'Ada', lastname: 'Lovelace' }]);
    analyticsService.summaryResponse = of([{ student_name: 'Ada Lovelace', course_title: 'Introduction to Africa', progress: 50, status: 'active', last_active: '2026-05-01T00:00:00.000Z' }]);
    analyticsService.runtimeSupportResponse = of([{
      student_id: 'student-1',
      student_name: 'Ada Lovelace',
      student_course_id: 'student-course-1',
      course_id: 'course-1',
      course_title: 'Introduction to Africa',
      support_state: 'remediation',
      support_summary: 'Recent evidence suggests the learner may benefit from brief review in Introduction to Africa.',
      evidence_source: 'recent_assessment_retry',
      recommended_action: 'review-and-continue',
      last_evidence_at: '2026-05-01T00:00:00.000Z',
      context_lesson_id: 'lesson-1',
      context_lesson_title: 'Introduction to Africa',
      context_key_concepts: ['continent', 'diversity'],
      context_prompts: ['Revisit one idea from Introduction to Africa.'],
      educator_intervention_hint: 'Offer a brief guided discussion.',
    }]);

    fixture.detectChanges();

    expect(analyticsService.getEducatorRuntimeSupport).toHaveBeenCalledWith('course-1');
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Runtime Support');
    expect(compiled.textContent).toContain('Needs review support');
    expect(compiled.textContent).toContain('Ada Lovelace');
    expect(compiled.textContent).toContain('Introduction to Africa');
    expect(compiled.textContent).toContain('Revisit one idea from Introduction to Africa.');
    expect(compiled.textContent).not.toContain('review-and-continue');
  });

  it('renders enrichment context with educator-safe summary', () => {
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Introduction to Africa', standards_metadata: { pathway_key: 'introduction-to-africa' } }]);
    usersService.studentsResponse = of([{ id: 'student-1', firstname: 'Biko', lastname: 'Extension' }]);
    analyticsService.summaryResponse = of([{ student_name: 'Biko Extension', course_title: 'Introduction to Africa', progress: 95, status: 'active', last_active: '2026-05-02T00:00:00.000Z' }]);
    analyticsService.runtimeSupportResponse = of([{
      student_id: 'student-1',
      student_name: 'Biko Extension',
      student_course_id: 'student-course-1',
      course_id: 'course-1',
      course_title: 'Introduction to Africa',
      support_state: 'enrichment',
      support_summary: 'Recent mastery evidence is strong enough to support optional enrichment.',
      evidence_source: 'strong_mastery_signal',
      recommended_action: 'continue-with-enrichment',
      last_evidence_at: '2026-05-02T00:00:00.000Z',
      context_lesson_id: 'lesson-1',
      context_lesson_title: 'Introduction to Africa',
      context_key_concepts: ['curiosity'],
      context_prompts: ['Look a little deeper at Introduction to Africa.'],
      educator_intervention_hint: null,
    }]);

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Ready for enrichment');
    expect(compiled.textContent).toContain('Recent mastery evidence is strong enough to support optional enrichment.');
    expect(compiled.textContent).toContain('Look a little deeper at Introduction to Africa.');
  });

  it('renders runtime support empty state when the flagship course has no support rows', () => {
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Introduction to Africa', standards_metadata: { pathway_key: 'introduction-to-africa' } }]);
    usersService.studentsResponse = of([{ id: 'student-1', firstname: 'Ada', lastname: 'Lovelace' }]);
    analyticsService.summaryResponse = of([]);
    analyticsService.runtimeSupportResponse = of([]);

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Runtime support will appear here');
  });

  it('renders runtime support error state and retries without introducing mutations', () => {
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Introduction to Africa', standards_metadata: { pathway_key: 'introduction-to-africa' } }]);
    usersService.studentsResponse = of([]);
    analyticsService.summaryResponse = of([]);
    analyticsService.runtimeSupportResponse = throwError(() => new Error('runtime failed'));

    fixture.detectChanges();

    expect(analyticsService.getEducatorRuntimeSupport).toHaveBeenCalledTimes(1);
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('We could not load learner support visibility');

    analyticsService.runtimeSupportResponse = of([]);
    const retryButton = Array.from(compiled.querySelectorAll('button')).find(
      (button) => button.textContent?.trim() === 'Retry'
    ) as HTMLButtonElement;
    retryButton.click();
    fixture.detectChanges();

    expect(analyticsService.getEducatorRuntimeSupport).toHaveBeenCalledTimes(2);
    expect(coursesService.assignCourseToStudent).not.toHaveBeenCalled();
    expect(coursesService.deleteCourse).not.toHaveBeenCalled();
  });
});
