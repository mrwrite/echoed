import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { Router } from '@angular/router';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { of, Subject, throwError } from 'rxjs';

import { LessonViewComponent } from './lesson-view.component';
import { CoursesService } from '../services/courses.service';

class MockCoursesService {
  getCurrentSegment = jasmine.createSpy('getCurrentSegment').and.returnValue(
    of({
      delivery_state: 'pending_review',
      detail: 'This lesson is waiting for governed approval.',
    }),
  );
  getLessonById = jasmine.createSpy('getLessonById');
  markSegmentCompleted = jasmine.createSpy('markSegmentCompleted');
  getCourses = jasmine.createSpy('getCourses');
  getCourseById = jasmine.createSpy('getCourseById');
  getStudentCourses = jasmine.createSpy('getStudentCourses');
}

describe('LessonViewComponent', () => {
  let component: LessonViewComponent;
  let fixture: ComponentFixture<LessonViewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CommonModule, RouterTestingModule, LessonViewComponent],
      providers: [
        { provide: CoursesService, useClass: MockCoursesService },
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              paramMap: {
                get: () => 'student-unit-1',
              },
            },
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(LessonViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('renders the canonical blocked state when governed delivery is unavailable', () => {
    const compiled = fixture.nativeElement as HTMLElement;

    expect(compiled.querySelector('[data-echo-state="blocked"]')).not.toBeNull();
    expect(compiled.textContent).toContain('This lesson is waiting for governed approval.');
    expect(compiled.textContent).toContain('Return to dashboard');
  });

  it('renders the canonical loading state while the lesson segment is resolving', async () => {
    const pendingSegment = new Subject<any>();
    const coursesService = TestBed.inject(CoursesService) as unknown as MockCoursesService;
    coursesService.getCurrentSegment.and.returnValue(pendingSegment.asObservable());

    fixture = TestBed.createComponent(LessonViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('[data-echo-loading="page"]')).not.toBeNull();
    expect(compiled.textContent).toContain('Preparing lesson delivery');
  });

  it('preserves the learner-safe exit control label used by the smoke flow', () => {
    const coursesService = TestBed.inject(CoursesService) as unknown as MockCoursesService;
    coursesService.getCurrentSegment.and.returnValue(of({
      delivery_state: 'governed_available',
      lesson_id: 'lesson-1',
      unit_progress_id: 'student-unit-1',
    }));
    coursesService.getLessonById.and.returnValue(of({
      id: 'lesson-1',
      title: 'Introduction to Africa',
      activities: [{ title: 'Warm Up', type: 'story', content: 'Read together.' }],
    }));

    fixture = TestBed.createComponent(LessonViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    const exitButton = Array.from(fixture.nativeElement.querySelectorAll('button'))
      .find((button) => (button as HTMLButtonElement).getAttribute('aria-label') === 'Exit lesson and return to dashboard') as HTMLButtonElement;

    expect(exitButton).not.toBeNull();
  });

  it('keeps lesson error and governed states labeled for assistive technology', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const blockedState = compiled.querySelector('[data-echo-state="blocked"]') as HTMLElement;
    expect(blockedState.getAttribute('aria-label')).toBe('governed-lesson-state');
  });

  it('renders a generic retryable error state when the governed segment cannot be restored', () => {
    const coursesService = TestBed.inject(CoursesService) as unknown as MockCoursesService;
    coursesService.getCurrentSegment.and.returnValue(throwError(() => new Error('segment failed')));

    fixture = TestBed.createComponent(LessonViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('[data-echo-state="error"]')).not.toBeNull();
    expect(compiled.textContent).toContain('We could not prepare this lesson');
    expect(compiled.textContent).toContain('Retry');
    expect(compiled.textContent).not.toContain('Course completed!');
  });

  it('recovers from a stale segment id by restoring the active student course progress', async () => {
    const coursesService = TestBed.inject(CoursesService) as unknown as MockCoursesService;
    const router = TestBed.inject(Router);
    spyOn(router, 'navigate').and.resolveTo(true);

    coursesService.getCurrentSegment.and.returnValues(
      throwError(() => ({ status: 404 })),
      of({
        delivery_state: 'governed_available',
        lesson_id: 'lesson-2',
        unit_progress_id: 'student-unit-2',
      }),
    );
    coursesService.getStudentCourses.and.returnValue(of([
      {
        unit_progress_id: 'student-unit-2',
        course: { title: 'Introduction to Africa' },
      },
    ] as any));
    coursesService.getLessonById.and.returnValue(of({
      id: 'lesson-2',
      title: 'Recovered lesson',
      activities: [],
    } as any));

    fixture = TestBed.createComponent(LessonViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    expect(coursesService.getCurrentSegment).toHaveBeenCalledWith('student-unit-1');
    expect(coursesService.getCurrentSegment).toHaveBeenCalledWith('student-unit-2');
    expect(router.navigate).toHaveBeenCalledWith(['../', 'student-unit-2'], { relativeTo: TestBed.inject(ActivatedRoute) });
    expect(component.loadErrorMessage).toBe('');
    expect(component.lesson?.title).toBe('Recovered lesson');
  });

  it('prefers the Introduction to Africa course for demo lessons', async () => {
    TestBed.resetTestingModule();
    await TestBed.configureTestingModule({
      imports: [CommonModule, RouterTestingModule, LessonViewComponent],
      providers: [
        { provide: CoursesService, useClass: MockCoursesService },
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              paramMap: {
                get: () => 'demo',
              },
            },
          },
        },
      ],
    }).compileComponents();

    const demoCoursesService = TestBed.inject(CoursesService) as unknown as MockCoursesService;
    demoCoursesService.getCourses.and.returnValue(of([
      { id: 'course-a', title: 'C', standards_metadata: {} },
      { id: 'course-b', title: 'Introduction to Africa', standards_metadata: { pathway_key: 'introduction-to-africa' } },
    ] as any));
    demoCoursesService.getCourseById.and.returnValue(of({
      units: [{
        lessons: [{
          id: 'lesson-1',
          title: 'Introduction to Africa',
          activities: [
            { title: 'Storybook', type: 'storybook', content: '', pages: [] },
          ],
        }],
      }],
    } as any));

    const demoFixture = TestBed.createComponent(LessonViewComponent);
    demoFixture.detectChanges();

    expect(demoCoursesService.getCourseById).toHaveBeenCalledWith('course-b');
  });
});
