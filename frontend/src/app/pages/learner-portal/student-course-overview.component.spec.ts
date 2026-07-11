import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { of, throwError } from 'rxjs';

import { StudentCourseOverviewComponent } from './student-course-overview.component';
import { CoursesService } from '../../services/courses.service';
import { ToastService } from '../../services/toast.service';
import { StudentCourseWithDetails } from '../../models/student-course-with-details.model';

const course = {
  id: 'course-1',
  title: 'Introduction to Africa',
  description: 'Explore geography, history, and community knowledge.',
  learning_objectives: 'Locate major regions and explain how communities shape history.',
  created_at: new Date(),
  units: [
    {
      id: 'unit-1',
      title: 'Place and People',
      order: 1,
      lessons: [
        {
          id: 'lesson-1',
          title: 'Mapping Africa',
          objective: 'Read a map with care.',
          order: 1,
          duration_minutes: 15,
          activities: [{ id: 'activity-1', title: 'Map check', type: 'quiz', content: '{}' }],
        },
        {
          id: 'lesson-2',
          title: 'Communities and History',
          order: 2,
          activities: [],
        },
      ],
    },
  ],
};

function enrolled(overrides: Partial<StudentCourseWithDetails> = {}): StudentCourseWithDetails {
  return {
    id: 'student-course-1',
    student_id: 'student-1',
    course_id: 'course-1',
    enrolled_on: '2026-01-01T00:00:00Z',
    status: 'active',
    course,
    unit_progress_id: 'unit-progress-1',
    progress: 0,
    ...overrides,
  };
}

class MockCoursesService {
  courseResponse = of(course);
  studentCoursesResponse = of([enrolled()]);
  progressResponse = of(25);
  segmentResponse = of({
    delivery_state: 'governed_available',
    lesson_id: 'lesson-1',
    unit_progress_id: 'unit-progress-1',
  });

  getCourseById = jasmine.createSpy('getCourseById').and.callFake(() => this.courseResponse);
  getStudentCourses = jasmine.createSpy('getStudentCourses').and.callFake(() => this.studentCoursesResponse);
  getCourseProgress = jasmine.createSpy('getCourseProgress').and.callFake(() => this.progressResponse);
  getCurrentSegment = jasmine.createSpy('getCurrentSegment').and.callFake(() => this.segmentResponse);
  enrollInCourse = jasmine.createSpy('enrollInCourse').and.returnValue(of({}));
  startCourse = jasmine.createSpy('startCourse').and.callFake(() => this.segmentResponse);
}

class MockToastService {
  show = jasmine.createSpy('show');
}

describe('StudentCourseOverviewComponent', () => {
  let fixture: ComponentFixture<StudentCourseOverviewComponent>;
  let component: StudentCourseOverviewComponent;
  let coursesService: MockCoursesService;
  let router: Router;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RouterTestingModule, StudentCourseOverviewComponent],
      providers: [
        { provide: CoursesService, useClass: MockCoursesService },
        { provide: ToastService, useClass: MockToastService },
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              paramMap: {
                get: () => 'course-1',
              },
            },
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(StudentCourseOverviewComponent);
    component = fixture.componentInstance;
    coursesService = TestBed.inject(CoursesService) as unknown as MockCoursesService;
    router = TestBed.inject(Router);
    spyOn(router, 'navigate').and.resolveTo(true);
    fixture.detectChanges();
  });

  it('loads the authorized course overview with unit hierarchy and current lesson state', () => {
    const compiled = fixture.nativeElement as HTMLElement;

    expect(coursesService.getCourseById).toHaveBeenCalledWith('course-1');
    expect(compiled.textContent).toContain('Introduction to Africa');
    expect(compiled.textContent).toContain('Place and People');
    expect(compiled.textContent).toContain('Mapping Africa');
    expect(compiled.textContent).toContain('In progress');
    expect(compiled.textContent).toContain('Locked');
    expect(component.curriculumUnits[0].lessons[0].canOpen).toBeTrue();
    expect(component.curriculumUnits[0].lessons[1].canOpen).toBeFalse();
  });

  it('resumes an in-progress course through the governed start-course endpoint', () => {
    component.performPrimaryAction();

    expect(coursesService.startCourse).toHaveBeenCalledWith({ course_id: 'course-1' });
    expect(router.navigate).toHaveBeenCalledWith(['/learn/lesson', 'unit-progress-1']);
  });

  it('enrolls before starting a not-started course', () => {
    coursesService.studentCoursesResponse = of([]);
    fixture = TestBed.createComponent(StudentCourseOverviewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    coursesService.studentCoursesResponse = of([enrolled()]);
    component.performPrimaryAction();

    expect(coursesService.enrollInCourse).toHaveBeenCalledWith('course-1');
    expect(coursesService.startCourse).toHaveBeenCalledWith({ course_id: 'course-1' });
  });

  it('does not mark completed courses incomplete or start another segment', () => {
    coursesService.studentCoursesResponse = of([enrolled({ status: 'completed', progress: 100 })]);
    fixture = TestBed.createComponent(StudentCourseOverviewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    component.performPrimaryAction();

    expect(coursesService.startCourse).not.toHaveBeenCalled();
    expect(component.actionMessage).toContain('complete');
  });

  it('renders invalid course id failures without changing progress', () => {
    coursesService.getCourseById.and.returnValue(throwError(() => ({ status: 400 })));
    fixture = TestBed.createComponent(StudentCourseOverviewComponent);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('This course link is not valid');
    expect(compiled.querySelector('[data-echo-state="error"]')).not.toBeNull();
  });
});
