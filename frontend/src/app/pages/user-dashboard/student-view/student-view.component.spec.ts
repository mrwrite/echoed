import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { of, Subject, throwError } from 'rxjs';

import { StudentViewComponent } from './student-view.component';
import { CoursesService } from '../../../services/courses.service';
import { AnalyticsService } from '../../../services/analytics.service';
import { BadgesService } from '../../../services/badges.service';
import { ProgramsService } from '../../../services/programs.service';
import { ToastService } from '../../../services/toast.service';
import { StudentCourseWithDetails } from '../../../models/student-course-with-details.model';

type StudentCourseOverride = Partial<StudentCourseWithDetails> & {
  title?: string;
  description?: string;
};

function buildStudentCourse(overrides: StudentCourseOverride = {}): StudentCourseWithDetails {
  return {
    id: overrides['id'] ?? 'student-course-1',
    student_id: 'student-1',
    course_id: overrides['course_id'] ?? overrides['id'] ?? 'course-1',
    enrolled_on: overrides['enrolled_on'] ?? '2026-01-01T00:00:00.000Z',
    status: overrides['status'] ?? 'enrolled',
    progress: overrides['progress'] ?? 0,
    unit_progress_id: overrides['unit_progress_id'] ?? 'unit-progress-1',
    continuation_guidance: overrides['continuation_guidance'] ?? null,
    course: {
      id: overrides['course_id'] ?? overrides['id'] ?? 'course-1',
      title: overrides['title'] ?? 'Course A',
      description: overrides['description'] ?? 'Course description',
      units: [],
      created_at: new Date('2026-01-01T00:00:00.000Z'),
    },
  };
}

class MockCoursesService {
  studentCoursesResponse = of<any[]>([]);
  availableCoursesResponse = of<any[]>([]);

  getStudentCourses = jasmine.createSpy('getStudentCourses').and.callFake(() => this.studentCoursesResponse);
  getCourseProgress = jasmine.createSpy('getCourseProgress').and.returnValue(of(0));
  getCourses = jasmine.createSpy('getCourses').and.callFake(() => this.availableCoursesResponse);
  startCourse = jasmine.createSpy('startCourse');
  enrollInCourse = jasmine.createSpy('enrollInCourse');
  markSegmentCompleted = jasmine.createSpy('markSegmentCompleted');
}

class MockAnalyticsService {
  getStudentProgress = jasmine.createSpy('getStudentProgress').and.returnValue(of({
    metrics: {
      lessons_completed: 0,
      units_completed: 0,
      courses_completed: 0,
      streak_days: 0,
    },
    badge_progress: [],
  }));
}

class MockBadgesService {
  getStudentBadges = jasmine.createSpy('getStudentBadges').and.returnValue(of([]));
}

class MockProgramsService {
  getPrograms = jasmine.createSpy('getPrograms').and.returnValue(of([]));
  getMyCertifications = jasmine.createSpy('getMyCertifications').and.returnValue(of([]));
}

class MockToastService {
  show = jasmine.createSpy('show');
}

describe('StudentViewComponent', () => {
  let component: StudentViewComponent;
  let fixture: ComponentFixture<StudentViewComponent>;
  let coursesService: MockCoursesService;
  let router: Router;

  async function createComponent() {
    await TestBed.configureTestingModule({
      imports: [RouterTestingModule, HttpClientTestingModule, StudentViewComponent],
      providers: [
        { provide: CoursesService, useClass: MockCoursesService },
        { provide: AnalyticsService, useClass: MockAnalyticsService },
        { provide: BadgesService, useClass: MockBadgesService },
        { provide: ProgramsService, useClass: MockProgramsService },
        { provide: ToastService, useClass: MockToastService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(StudentViewComponent);
    component = fixture.componentInstance;
    component.userInfo = { fullname: 'Test User', role: 'student', user_id: 'student-1' } as any;
    coursesService = TestBed.inject(CoursesService) as unknown as MockCoursesService;
    router = TestBed.inject(Router);
  }

  beforeEach(async () => {
    await createComponent();
  });

  it('selects an in-progress course over the first course in the list', () => {
    coursesService.studentCoursesResponse = of([
      buildStudentCourse({ id: 'course-completed', title: 'Completed First', status: 'completed', progress: 100 }),
      buildStudentCourse({
        id: 'course-active',
        title: 'Active Second',
        status: 'active',
        progress: 32,
        continuation_guidance: {
          support_state: 'normal',
          learner_title: 'Your next lesson is ready',
          learner_message: 'Continue where you already have momentum.',
          recommended_action: 'continue',
          evidence_source: 'governed_continuation',
        } as any,
      }),
    ]);

    fixture.detectChanges();

    expect(component.activeStudentCourse?.course.title).toBe('Active Second');
    expect(component.activeStudentCourseReason).toContain('momentum');
  });

  it('selects the earliest in-progress course deterministically when multiple are active', () => {
    coursesService.studentCoursesResponse = of([
      buildStudentCourse({ id: 'course-later', title: 'Later Active', status: 'active', enrolled_on: '2026-03-01T00:00:00.000Z' }),
      buildStudentCourse({ id: 'course-earlier', title: 'Earlier Active', status: 'active', enrolled_on: '2026-01-01T00:00:00.000Z' }),
    ]);

    fixture.detectChanges();

    expect(component.activeStudentCourse?.course.title).toBe('Earlier Active');
  });

  it('uses deterministic fallback when no course is in progress', () => {
    coursesService.studentCoursesResponse = of([
      buildStudentCourse({ id: 'course-late', title: 'Zulu Studies', enrolled_on: '2026-03-01T00:00:00.000Z', progress: 0 }),
      buildStudentCourse({ id: 'course-early', title: 'African History', enrolled_on: '2026-01-01T00:00:00.000Z', progress: 0 }),
    ]);

    fixture.detectChanges();

    expect(component.activeStudentCourse?.course.title).toBe('African History');
    expect(component.activeStudentCourseReason).toContain('Next recommended course');
  });

  it('renders empty state when no courses exist', () => {
    coursesService.studentCoursesResponse = of([]);

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('[data-echo-state="empty"]')).not.toBeNull();
    expect(compiled.textContent).toContain('Your learning path will appear here');
  });

  it('renders error and retry state when course data fails to load', () => {
    spyOn(console, 'error');
    coursesService.studentCoursesResponse = throwError(() => new Error('load failed'));

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('[data-echo-state="error"]')).not.toBeNull();
    expect(compiled.textContent).toContain('We could not load your courses');
    expect(compiled.textContent).toContain('Retry');
  });

  it('retries course loading from the error state action', () => {
    spyOn(console, 'error');
    coursesService.studentCoursesResponse = throwError(() => new Error('load failed'));

    fixture.detectChanges();
    expect(coursesService.getStudentCourses).toHaveBeenCalledTimes(1);

    coursesService.studentCoursesResponse = of([
      buildStudentCourse({ id: 'course-retry', title: 'Recovered Course', status: 'active', progress: 12 }),
    ]);

    const buttons = Array.from(
      fixture.nativeElement.querySelectorAll('button'),
    ) as HTMLButtonElement[];
    const retryAction = buttons.find((button) => button.textContent?.trim() === 'Retry') as HTMLButtonElement;

    retryAction.click();
    fixture.detectChanges();

    expect(coursesService.getStudentCourses).toHaveBeenCalledTimes(2);
    expect(component.activeStudentCourse?.course.title).toBe('Recovered Course');
    expect(component.coursesLoadError).toBe('');
  });

  it('renders loading state with EchoLoadingState before courses resolve', () => {
    const pendingCourses = new Subject<any[]>();
    coursesService.studentCoursesResponse = pendingCourses.asObservable();

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('[data-echo-loading="compact"]')).not.toBeNull();
    expect(compiled.querySelector('[data-echo-loading="section"]')).not.toBeNull();
  });

  it('renders clean demo-facing copy without mojibake artifacts', () => {
    coursesService.studentCoursesResponse = of([
      buildStudentCourse({ id: 'course-active', title: 'Introduction to Africa', status: 'active', progress: 42 }),
    ]);

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Here is a guided overview of your EchoEd learning journey.');
    expect(compiled.textContent).toContain('K-5 Demo');
    expect(compiled.textContent).toContain("What's next");
    expect(compiled.textContent).toContain('Completed "Roots of Rhythm" lesson');
    expect(compiled.textContent).not.toContain('â');
    expect(compiled.textContent).not.toContain('ðŸ');
  });

  it('uses the explicit selected continuation course for the CTA', () => {
    coursesService.studentCoursesResponse = of([
      buildStudentCourse({
        id: 'course-active',
        title: 'Active Learning Path',
        status: 'active',
        progress: 55,
        continuation_guidance: {
          support_state: 'normal',
          learner_title: 'Your next lesson is ready',
          learner_message: 'Keep your momentum with the next governed lesson.',
          reinforcement_title: 'Steady progress matters',
          reinforcement_message: 'Your effort is adding up. Keep going with care, and let each lesson strengthen what you know.',
          recommended_action: 'continue',
          evidence_source: 'governed_continuation',
        } as any,
      }),
    ]);

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Active Learning Path');
    expect(compiled.textContent).toContain('In progress');
    expect(compiled.textContent).toContain('Selected continuation');
    expect(compiled.textContent).toContain('Your next lesson is ready');
    expect(compiled.textContent).toContain('Keep your momentum with the next governed lesson.');
    expect(compiled.textContent).toContain('Steady progress matters');
    expect(compiled.textContent).toContain('Your effort is adding up.');
    expect(compiled.textContent).toContain('Governed course progress');
    expect(compiled.textContent).toContain('saves progress automatically');
  });

  it('renders remediation-aware continuation guidance when present', () => {
    coursesService.studentCoursesResponse = of([
      buildStudentCourse({
        id: 'course-remediation',
        title: 'Supportive Path',
        status: 'active',
        continuation_guidance: {
          support_state: 'remediation',
          learner_title: 'Take your next step with support',
          learner_message: 'Your next lesson is still ready. Revisit the last check and use the support prompts to rebuild confidence.',
          reinforcement_title: 'Learning can be rebuilt',
          reinforcement_message: 'A hard moment does not erase your progress. Review one idea at a time, then keep moving with support.',
          recommended_action: 'review-and-continue',
          evidence_source: 'recent_assessment_retry',
          review_lesson_title: 'Introduction to Africa',
          review_key_concepts: ['continent', 'regions'],
          review_prompts: ['Say, draw, or write one idea from Introduction to Africa that you want to remember.'],
        } as any,
      }),
    ]);

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Supportive next step');
    expect(compiled.textContent).toContain('Take your next step with support');
    expect(compiled.textContent).toContain('rebuild confidence');
    expect(compiled.textContent).toContain('Learning can be rebuilt');
    expect(compiled.textContent).toContain('does not erase your progress');
    expect(compiled.textContent).toContain('Helpful review before you continue');
    expect(compiled.textContent).toContain('Revisit Introduction to Africa');
    expect(compiled.textContent).toContain('continent');
  });

  it('renders enrichment-aware continuation guidance when present', () => {
    coursesService.studentCoursesResponse = of([
      buildStudentCourse({
        id: 'course-enrichment',
        title: 'Deepening Path',
        status: 'active',
        continuation_guidance: {
          support_state: 'enrichment',
          learner_title: 'You are ready for a deeper challenge',
          learner_message: 'Continue with your next governed lesson and, if you want an extra stretch, revisit Introduction to Africa for optional extension prompts that deepen your thinking.',
          reinforcement_title: 'Your understanding is growing strong',
          reinforcement_message: 'You have earned an optional deeper look. Follow your curiosity without leaving your steady learning path.',
          recommended_action: 'continue-with-enrichment',
          evidence_source: 'strong_mastery_signal',
          extension_lesson_title: 'Introduction to Africa',
          extension_key_concepts: ['continent', 'diversity'],
          extension_prompts: ['Look a little deeper at Introduction to Africa by connecting one lesson idea to a place, community, or question you want to explore next.'],
        } as any,
      }),
    ]);

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Recommended enrichment');
    expect(compiled.textContent).toContain('deeper challenge');
    expect(compiled.textContent).toContain('Your understanding is growing strong');
    expect(compiled.textContent).toContain('Follow your curiosity');
    expect(compiled.textContent).toContain('Optional deeper exploration');
    expect(compiled.textContent).toContain('Extend Introduction to Africa');
    expect(compiled.textContent).toContain('continent');
  });

  it('shows encouraging completion copy when all enrolled courses are complete', () => {
    coursesService.studentCoursesResponse = of([
      buildStudentCourse({ id: 'course-completed', title: 'Finished Path', status: 'completed', progress: 100 }),
    ]);

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('You completed your current learning path');
    expect(compiled.textContent).toContain('celebrate your growth');
  });

  it('does not render staff publish readiness UI on the learner dashboard', () => {
    coursesService.studentCoursesResponse = of([
      buildStudentCourse({ id: 'course-active', title: 'Learner Course', status: 'active', progress: 40 }),
    ]);

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).not.toContain('Publish readiness');
    expect(compiled.textContent).not.toContain('Blocking issues');
    expect(compiled.textContent).not.toContain('Safe publish validation');
    expect(compiled.textContent).not.toContain('Not safe');
    expect(compiled.textContent).not.toContain('Competency evidence integrity');
    expect(compiled.textContent).not.toContain('Explainable');
    expect(compiled.textContent).not.toContain('Affected competencies');
    expect(compiled.textContent).not.toContain('Runtime intervention recommendations');
    expect(compiled.textContent).not.toContain('Learner-safe message');
    expect(compiled.textContent).not.toContain('Caution flags');
  });

  it('keeps the continue lesson action bound to the selected course during enrichment guidance', () => {
    const enrichmentCourse = buildStudentCourse({
      id: 'course-enrichment',
      title: 'Deepening Path',
      status: 'active',
      continuation_guidance: {
        support_state: 'enrichment',
        learner_title: 'You are ready for a deeper challenge',
        learner_message: 'Continue with your next governed lesson and, if you want an extra stretch, revisit Introduction to Africa for optional extension prompts that deepen your thinking.',
        recommended_action: 'continue-with-enrichment',
        evidence_source: 'strong_mastery_signal',
        extension_lesson_title: 'Introduction to Africa',
        extension_prompts: ['Look a little deeper at Introduction to Africa by connecting one lesson idea to a place, community, or question you want to explore next.'],
      } as any,
    });
    coursesService.studentCoursesResponse = of([enrichmentCourse]);
    spyOn(component, 'startCourse');

    fixture.detectChanges();

    const buttons = Array.from(
      fixture.nativeElement.querySelectorAll('button'),
    ) as HTMLButtonElement[];
    const continueAction = buttons.find((button) => button.textContent?.trim() === 'Continue lesson') as HTMLButtonElement;

    continueAction.click();

    expect(component.startCourse).toHaveBeenCalledWith(enrichmentCourse);
  });

  it('routes catalog actions from the empty continuation state', () => {
    spyOn(router, 'navigate');
    coursesService.studentCoursesResponse = of([]);

    fixture.detectChanges();

    const buttons = Array.from(
      fixture.nativeElement.querySelectorAll('button'),
    ) as HTMLButtonElement[];
    const action = buttons.find((button) => button.textContent?.trim() === 'Explore catalog') as HTMLButtonElement;

    action.click();

    expect(router.navigate).toHaveBeenCalledWith(['/learn/products']);
  });

  it('keeps the continue lesson action bound to the selected course during remediation guidance', () => {
    const remediationCourse = buildStudentCourse({
      id: 'course-remediation',
      title: 'Supportive Path',
      status: 'active',
      continuation_guidance: {
        support_state: 'remediation',
        learner_title: 'Take your next step with support',
        learner_message: 'Your next lesson is still ready.',
        recommended_action: 'review-and-continue',
        evidence_source: 'recent_assessment_retry',
        review_lesson_title: 'Introduction to Africa',
        review_prompts: ['Review one map idea before continuing.'],
      } as any,
    });
    coursesService.studentCoursesResponse = of([remediationCourse]);
    spyOn(component, 'startCourse');

    fixture.detectChanges();

    const buttons = Array.from(
      fixture.nativeElement.querySelectorAll('button'),
    ) as HTMLButtonElement[];
    const continueAction = buttons.find((button) => button.textContent?.trim() === 'Continue lesson') as HTMLButtonElement;

    continueAction.click();

    expect(component.startCourse).toHaveBeenCalledWith(remediationCourse);
  });

  it('uses clearer start and resume labels for course cards', () => {
    coursesService.studentCoursesResponse = of([
      buildStudentCourse({ id: 'course-start', title: 'New Course', status: 'enrolled', progress: 0 }),
      buildStudentCourse({ id: 'course-resume', title: 'Resume Course', status: 'active', progress: 24 }),
    ]);

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Start course');
    expect(compiled.textContent).toContain('Resume lesson');
  });
});
