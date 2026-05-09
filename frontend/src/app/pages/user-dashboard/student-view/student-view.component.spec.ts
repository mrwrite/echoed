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
      buildStudentCourse({ id: 'course-active', title: 'Active Second', status: 'active', progress: 32 }),
    ]);

    fixture.detectChanges();

    expect(component.activeStudentCourse?.course.title).toBe('Active Second');
    expect(component.activeStudentCourseReason).toContain('momentum');
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
    coursesService.studentCoursesResponse = throwError(() => new Error('load failed'));

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('[data-echo-state="error"]')).not.toBeNull();
    expect(compiled.textContent).toContain('We could not load your courses');
    expect(compiled.textContent).toContain('Retry');
  });

  it('retries course loading from the error state action', () => {
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

  it('uses the explicit selected continuation course for the CTA', () => {
    coursesService.studentCoursesResponse = of([
      buildStudentCourse({ id: 'course-active', title: 'Active Learning Path', status: 'active', progress: 55 }),
    ]);

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Active Learning Path');
    expect(compiled.textContent).toContain('Selected continuation');
    expect(compiled.textContent).toContain('Continue where you already have momentum.');
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

    expect(router.navigate).toHaveBeenCalledWith(['/home/courses']);
  });
});
