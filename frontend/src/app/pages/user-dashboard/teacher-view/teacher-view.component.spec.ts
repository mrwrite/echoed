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
  deleteCourse = jasmine.createSpy('deleteCourse').and.returnValue(of({}));
  assignCourseToStudent = jasmine.createSpy('assignCourseToStudent').and.returnValue(of({}));
}

class MockAnalyticsService {
  summaryResponse = of<any[]>([]);
  getTeacherSummary = jasmine.createSpy('getTeacherSummary').and.callFake(() => this.summaryResponse);
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
    coursesService.coursesResponse = pendingCourses.asObservable();
    usersService.studentsResponse = pendingStudents.asObservable();
    analyticsService.summaryResponse = pendingSummary.asObservable();

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('[data-echo-loading="section"]')).not.toBeNull();
    expect(compiled.textContent).toContain('Loading course management');
    expect(compiled.textContent).toContain('Loading student progress');
  });

  it('uses EchoStatePanel for teacher empty states', () => {
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const emptyStates = compiled.querySelectorAll('[data-echo-state="empty"]');
    expect(emptyStates.length).toBeGreaterThan(0);
    expect(compiled.textContent).toContain('Course management will appear here');
    expect(compiled.textContent).toContain('Student progress will appear here');
  });

  it('uses EchoStatePanel for teacher error states and retries data loads', () => {
    coursesService.coursesResponse = throwError(() => new Error('courses failed'));
    usersService.studentsResponse = throwError(() => new Error('students failed'));
    analyticsService.summaryResponse = throwError(() => new Error('summary failed'));

    fixture.detectChanges();
    expect(coursesService.getCourses).toHaveBeenCalledTimes(1);
    expect(usersService.getStudents).toHaveBeenCalledTimes(1);
    expect(analyticsService.getTeacherSummary).toHaveBeenCalledTimes(1);

    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Algebra I' }]);
    usersService.studentsResponse = of([{ id: 'student-1', firstname: 'Ada', lastname: 'Lovelace' }]);
    analyticsService.summaryResponse = of([{ student_name: 'Ada Lovelace', course_title: 'Algebra I', progress: 50, status: 'active', last_active: '2026-05-01T00:00:00.000Z' }]);

    const buttons = Array.from(fixture.nativeElement.querySelectorAll('button')) as HTMLButtonElement[];
    const retryLabels = ['Retry'];
    buttons.filter((button) => retryLabels.includes(button.textContent?.trim() || '')).forEach((button) => button.click());
    fixture.detectChanges();

    expect(coursesService.getCourses).toHaveBeenCalledTimes(3);
    expect(usersService.getStudents).toHaveBeenCalledTimes(2);
    expect(analyticsService.getTeacherSummary).toHaveBeenCalledTimes(2);
  });

  it('keeps existing teacher actions and links present', () => {
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Algebra I' }]);
    usersService.studentsResponse = of([{ id: 'student-1', firstname: 'Ada', lastname: 'Lovelace' }]);
    analyticsService.summaryResponse = of([{ student_name: 'Ada Lovelace', course_title: 'Algebra I', progress: 50, status: 'active', last_active: '2026-05-01T00:00:00.000Z' }]);

    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Add Course');
    expect(compiled.textContent).toContain('Assign Course');
    expect(compiled.textContent).toContain('Start Live Lesson');
    expect(compiled.textContent).toContain('View Reports');
  });

  it('renders responsive fallback markup for educator tables', () => {
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Algebra I' }]);
    usersService.studentsResponse = of([{ id: 'student-1', firstname: 'Ada', lastname: 'Lovelace' }]);
    analyticsService.summaryResponse = of([{ student_name: 'Ada Lovelace', course_title: 'Algebra I', progress: 50, status: 'active', last_active: '2026-05-01T00:00:00.000Z' }]);

    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('[data-educator-responsive="teacher-courses"]')).not.toBeNull();
    expect(compiled.querySelector('[data-educator-responsive="teacher-summary"]')).not.toBeNull();
  });
});
