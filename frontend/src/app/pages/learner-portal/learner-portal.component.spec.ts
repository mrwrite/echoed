import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { BehaviorSubject, of, throwError } from 'rxjs';

import { LearnerPortalComponent } from './learner-portal.component';
import { AnalyticsService } from '../../services/analytics.service';
import { BadgesService } from '../../services/badges.service';
import { CoursesService } from '../../services/courses.service';
import { PermissionsService } from '../../services/permissions.service';
import { ProgramsService } from '../../services/programs.service';
import { ToastService } from '../../services/toast.service';
import { V2PlatformService } from '../../services/v2-platform.service';
import { StudentCourseWithDetails } from '../../models/student-course-with-details.model';

function makeStudentCourse(overrides: Partial<StudentCourseWithDetails> = {}): StudentCourseWithDetails {
  return {
    id: 'student-course-1',
    student_id: 'student-1',
    course_id: 'course-1',
    enrolled_on: '2026-01-01T00:00:00Z',
    status: 'active',
    progress: 42,
    course: {
      id: 'course-1',
      title: 'Introduction to Africa',
      description: 'Explore geography, history, and community knowledge.',
      created_at: new Date(),
      units: [],
    },
    unit_progress_id: 'unit-progress-1',
    continuation_guidance: {
      support_state: 'normal',
      learner_title: 'Your next lesson is ready',
      learner_message: 'Continue where you already have momentum.',
      recommended_action: 'continue',
      evidence_source: 'current_progress',
    },
    ...overrides,
  };
}

class MockCoursesService {
  studentCoursesResponse = of([makeStudentCourse()]);
  coursesResponse = of([
    {
      id: 'course-2',
      title: 'African Kingdoms',
      description: 'Learn about trade, leadership, and daily life.',
      created_at: new Date(),
      units: [],
    },
  ]);
  getStudentCourses = jasmine.createSpy('getStudentCourses').and.callFake(() => this.studentCoursesResponse);
  getCourseProgress = jasmine.createSpy('getCourseProgress').and.returnValue(of(42));
  getCourses = jasmine.createSpy('getCourses').and.callFake(() => this.coursesResponse);
  startCourse = jasmine.createSpy('startCourse').and.returnValue(of({
    delivery_state: 'governed_available',
    unit_progress_id: 'unit-progress-1',
    lesson_id: 'lesson-1',
  }));
  enrollInCourse = jasmine.createSpy('enrollInCourse').and.returnValue(of({}));
}

class MockAnalyticsService {
  getStudentProgress = jasmine.createSpy('getStudentProgress').and.returnValue(of({
    metrics: {
      lessons_completed: 3,
      units_completed: 1,
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

class MockV2PlatformService {
  productsResponse = of([]);
  getLearnerProducts = jasmine.createSpy('getLearnerProducts').and.callFake(() => this.productsResponse);
}

class MockPermissionsService {
  user$ = new BehaviorSubject<any>({ user_id: 'student-1', role: 'student' });
}

class MockToastService {
  show = jasmine.createSpy('show');
}

describe('LearnerPortalComponent', () => {
  let fixture: ComponentFixture<LearnerPortalComponent>;
  let component: LearnerPortalComponent;
  let coursesService: MockCoursesService;
  let router: Router;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RouterTestingModule, LearnerPortalComponent],
      providers: [
        { provide: CoursesService, useClass: MockCoursesService },
        { provide: AnalyticsService, useClass: MockAnalyticsService },
        { provide: BadgesService, useClass: MockBadgesService },
        { provide: ProgramsService, useClass: MockProgramsService },
        { provide: PermissionsService, useClass: MockPermissionsService },
        { provide: ToastService, useClass: MockToastService },
        { provide: V2PlatformService, useClass: MockV2PlatformService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(LearnerPortalComponent);
    component = fixture.componentInstance;
    coursesService = TestBed.inject(CoursesService) as unknown as MockCoursesService;
    router = TestBed.inject(Router);
    spyOn(router, 'navigate').and.resolveTo(true);
    fixture.detectChanges();
  });

  it('renders /learn as a learner-first home with the next action first', () => {
    const compiled = fixture.nativeElement as HTMLElement;

    expect(compiled.querySelector('h1')?.textContent).toContain('Continue your learning');
    expect(compiled.textContent).toContain('Next learning');
    expect(compiled.textContent).toContain('Introduction to Africa');
    expect(compiled.textContent).toContain('Continue where you already have momentum.');
    expect(compiled.textContent).not.toContain('Your products and learning paths');
  });

  it('prioritizes active student courses over available learning', () => {
    expect(component.activeStudentCourse?.course.title).toBe('Introduction to Africa');
    expect(component.continuationTitle).toBe('Introduction to Africa');
    expect(component.activeCourseStatusLabel).toBe('In progress');
  });

  it('fills progress bars to the normalized percentage width', () => {
    fixture.detectChanges();

    const activeProgressBar = fixture.nativeElement.querySelector('[aria-label="Active course progress"]') as HTMLElement;
    expect(activeProgressBar.style.width).toBe('42%');
    expect(activeProgressBar.getAttribute('aria-valuenow')).toBe('42');
  });

  it('normalizes fractional progress values before rendering width', () => {
    expect(component.normalizedProgress(0.42)).toBe(42);
    expect(component.progressWidth(0.42)).toBe('42%');
  });

  it('navigates course continuation through the canonical /learn lesson route', () => {
    component.startCourse(makeStudentCourse());

    expect(coursesService.startCourse).toHaveBeenCalledWith({ course_id: 'course-1' });
    expect(router.navigate).toHaveBeenCalledWith(['/learn/lesson', 'unit-progress-1']);
  });

  it('renders the no-active-course state without inventing assignments', () => {
    coursesService.studentCoursesResponse = of([]);
    coursesService.coursesResponse = of([]);

    fixture = TestBed.createComponent(LearnerPortalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Your next lesson will appear here');
    expect(compiled.textContent).toContain('When a course is assigned or you start a course');
  });

  it('renders available course cards from the existing course catalog', () => {
    const compiled = fixture.nativeElement as HTMLElement;

    expect(compiled.textContent).toContain('Available learning');
    expect(compiled.textContent).toContain('African Kingdoms');
    expect(compiled.textContent).toContain('Start course');
  });

  it('renders a recoverable course load error state', () => {
    coursesService.studentCoursesResponse = throwError(() => new Error('load failed'));

    fixture = TestBed.createComponent(LearnerPortalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('[data-echo-state="error"]')).not.toBeNull();
    expect(compiled.textContent).toContain('We could not restore your learning');
  });
});
