import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { of, Subject } from 'rxjs';

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
});
