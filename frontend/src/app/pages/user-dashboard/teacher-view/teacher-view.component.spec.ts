import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { of, Subject, throwError } from 'rxjs';

import { TeacherViewComponent } from './teacher-view.component';
import { CoursesService } from '../../../services/courses.service';
import { AnalyticsService } from '../../../services/analytics.service';
import { UsersService } from '../../../services/users.service';
import { ToastService } from '../../../services/toast.service';

class MockCoursesService {
  coursesResponse = of<any[]>([]);
  governanceSummaryResponse = of<any>(buildGovernanceSummary());
  getCourses = jasmine.createSpy('getCourses').and.callFake(() => this.coursesResponse);
  getCourseGovernanceSummary = jasmine.createSpy('getCourseGovernanceSummary').and.callFake(() => this.governanceSummaryResponse);
  getCoursePublishReadiness = jasmine.createSpy('getCoursePublishReadiness').and.returnValue(of({}));
  getCourseSafePublishValidation = jasmine.createSpy('getCourseSafePublishValidation').and.returnValue(of({}));
  getCourseCompetencyEvidenceIntegrity = jasmine.createSpy('getCourseCompetencyEvidenceIntegrity').and.returnValue(of({}));
  getCourseRuntimeInterventionRecommendations = jasmine.createSpy('getCourseRuntimeInterventionRecommendations').and.returnValue(of([]));
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

function buildGovernanceSummary(overrides: Partial<any> = {}) {
  return {
    course_id: 'course-1',
    course_title: 'Introduction to Africa',
    publish_readiness: { course_id: 'course-1', course_title: 'Introduction to Africa', is_ready: true, blocking_issue_count: 0, warning_count: 0, blocking_issues: [], warnings: [] },
    safe_publish_validation: { course_id: 'course-1', course_title: 'Introduction to Africa', is_safe: true, blocking_issue_count: 0, warning_count: 0, blocking_issues: [], warnings: [] },
    lineage_safety_visibility: { course_id: 'course-1', course_title: 'Introduction to Africa', is_coherent: true, is_safe: true, blocking_issue_count: 0, warning_count: 0, blocking_issues: [], warnings: [] },
    competency_evidence_integrity: { course_id: 'course-1', course_title: 'Introduction to Africa', is_valid: true, is_explainable: true, blocking_issue_count: 0, warning_count: 0, blocking_issues: [], warnings: [], affected_assessments: [], affected_competency_identifiers: [] },
    runtime_intervention_recommendations: [],
    ...overrides,
  };
}

describe('TeacherViewComponent', () => {
  let component: TeacherViewComponent;
  let fixture: ComponentFixture<TeacherViewComponent>;
  let coursesService: MockCoursesService;
  let analyticsService: MockAnalyticsService;
  let usersService: MockUsersService;
  let toastService: MockToastService;

  async function createComponent(role = 'teacher') {
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
    component.userInfo = { fullname: 'Teacher Test', role } as any;
    coursesService = TestBed.inject(CoursesService) as unknown as MockCoursesService;
    analyticsService = TestBed.inject(AnalyticsService) as unknown as MockAnalyticsService;
    usersService = TestBed.inject(UsersService) as unknown as MockUsersService;
    toastService = TestBed.inject(ToastService) as unknown as MockToastService;
  }

  beforeEach(async () => {
    await createComponent();
  });

  function text(): string {
    return (fixture.nativeElement as HTMLElement).textContent || '';
  }

  it('renders the canonical Teach overview for teacher state', () => {
    fixture.detectChanges();
    expect(text()).toContain('EchoEd Teach');
    expect(text()).toContain('Today in Teach');
    expect(text()).toContain('My classes');
    expect(text()).toContain('Browse curriculum');
    expect(text()).toContain('Assignments');
  });

  it('renders the same Teach overview for instructor-compatible state', async () => {
    TestBed.resetTestingModule();
    await createComponent('instructor');
    fixture.detectChanges();
    expect(text()).toContain('Today in Teach');
    expect(component.userInfo.role).toBe('instructor');
  });

  it('uses shared loading states while teacher data is loading', () => {
    coursesService.coursesResponse = new Subject<any[]>().asObservable();
    usersService.studentsResponse = new Subject<any[]>().asObservable();
    analyticsService.summaryResponse = new Subject<any[]>().asObservable();
    fixture.detectChanges();
    expect(text()).toContain('Loading learner progress');
    expect(text()).toContain('Loading curriculum');
  });

  it('renders no classes and no assignments entry state without inventing counts', () => {
    fixture.detectChanges();
    expect(text()).toContain('No progress yet');
    expect(text()).toContain('No curriculum is available');
    expect(text()).toContain('Create or inspect assignments');
  });

  it('renders needs-review limitations from supported data only', () => {
    fixture.detectChanges();
    expect(text()).toContain('Feedback, manual scoring, and discussion moderation are shown only where current APIs support them.');
    expect(text()).toContain('thread and post APIs exist, but they are not scoped to classes or moderation permissions.');
  });

  it('renders API failure states and retry actions', () => {
    coursesService.coursesResponse = throwError(() => new Error('courses failed'));
    analyticsService.summaryResponse = throwError(() => new Error('summary failed'));
    fixture.detectChanges();
    expect(text()).toContain('We could not load learner progress');
    expect(text()).toContain('We could not load courses');
    expect((fixture.nativeElement as HTMLElement).querySelectorAll('button').length).toBeGreaterThan(0);
  });

  it('keeps unauthorized/admin and Studio links out of teacher navigation content', () => {
    fixture.detectChanges();
    expect(text()).not.toContain('Admin Overview');
    expect(text()).not.toContain('Content Studio');
    expect(text()).not.toContain('Product Studio');
  });

  it('renders learner progress rows with consistent state language', () => {
    analyticsService.summaryResponse = of([{ student_name: 'Ada Lovelace', course_title: 'Introduction to Africa', progress: 45, status: 'active', last_active: '2026-05-01T00:00:00.000Z' }]);
    fixture.detectChanges();
    expect(text()).toContain('Ada Lovelace');
    expect(text()).toContain('Introduction to Africa');
    expect(text()).toContain('45%');
    expect(text()).toContain('In progress');
  });

  it('renders not-started language for missing activity dates', () => {
    analyticsService.summaryResponse = of([{ student_name: 'Biko Student', course_title: 'History', progress: 0, status: 'pending', last_active: null }]);
    fixture.detectChanges();
    expect(text()).toContain('No recent activity available');
    expect(text()).toContain('Pending');
  });

  it('calculates active learning and average completion from teacher summary rows', () => {
    analyticsService.summaryResponse = of([
      { student_name: 'One', course_title: 'Course', progress: 50, status: 'active', last_active: null },
      { student_name: 'Two', course_title: 'Course', progress: 100, status: 'completed', last_active: null },
    ]);
    fixture.detectChanges();
    expect(text()).toContain('Active learning1');
    expect(text()).toContain('Average progress75%');
  });

  it('renders curriculum cards with preview and assign actions', () => {
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Introduction to Africa', description: 'Course description', standards_metadata: { pathway_key: 'introduction-to-africa' } }]);
    fixture.detectChanges();
    expect(text()).toContain('Introduction to Africa');
    expect(text()).toContain('Course description');
    expect(text()).toContain('Preview course');
    expect(text()).toContain('Assign learning');
  });

  it('does not call student progress creation APIs from the overview', () => {
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Introduction to Africa', standards_metadata: { pathway_key: 'introduction-to-africa' } }]);
    fixture.detectChanges();
    expect(coursesService.getCourses).toHaveBeenCalled();
    expect(coursesService.assignCourseToStudent).not.toHaveBeenCalled();
    expect(coursesService.deleteCourse).not.toHaveBeenCalled();
  });

  it('still loads flagship runtime support for supported educator guidance data', () => {
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Introduction to Africa', standards_metadata: { pathway_key: 'introduction-to-africa' } }]);
    fixture.detectChanges();
    expect(analyticsService.getEducatorRuntimeSupport).toHaveBeenCalledWith('course-1');
  });

  it('handles course governance summary failures without exposing governance UI', () => {
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Introduction to Africa', standards_metadata: { pathway_key: 'introduction-to-africa' } }]);
    coursesService.governanceSummaryResponse = throwError(() => new Error('governance failed'));
    fixture.detectChanges();
    expect(coursesService.getCourseGovernanceSummary).toHaveBeenCalledWith('course-1');
    expect(text()).not.toContain('Safe publish validation');
  });

  it('uses responsive educator data-list markers for progress and courses', () => {
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Introduction to Africa' }]);
    analyticsService.summaryResponse = of([{ student_name: 'Ada Lovelace', course_title: 'Course', progress: 40, status: 'active', last_active: null }]);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('[data-educator-responsive="teacher-summary"]')).not.toBeNull();
    expect(compiled.querySelector('[data-educator-responsive="teacher-courses"]')).not.toBeNull();
  });

  it('refreshes teacher summary from the visible Refresh control', () => {
    fixture.detectChanges();
    const refresh = Array.from((fixture.nativeElement as HTMLElement).querySelectorAll('button')).find(button => button.textContent?.trim() === 'Refresh') as HTMLButtonElement;
    refresh.click();
    expect(analyticsService.getTeacherSummary).toHaveBeenCalledTimes(2);
  });

  it('validates quick assignment action without duplicate submission', () => {
    component.assignCourse();
    expect(toastService.show).toHaveBeenCalledWith('Select a student and a course to assign.', 'info');
    expect(coursesService.assignCourseToStudent).not.toHaveBeenCalled();
  });

  it('assigns a course only when a student and course are selected', () => {
    component.selectedCourseId = 'course-1';
    component.selectedStudentId = 'student-1';
    component.assignCourse();
    expect(coursesService.assignCourseToStudent).toHaveBeenCalledWith('course-1', 'student-1');
    expect(analyticsService.getTeacherSummary).toHaveBeenCalled();
  });

  it('reports assignment API failure without clearing selected values first', () => {
    coursesService.assignCourseToStudent.and.returnValue(throwError(() => ({ error: { detail: 'Assignment failed.' } })));
    component.selectedCourseId = 'course-1';
    component.selectedStudentId = 'student-1';
    component.assignCourse();
    expect(toastService.show).toHaveBeenCalledWith('Assignment failed.', 'error');
    expect(component.selectedCourseId).toBe('course-1');
    expect(component.selectedStudentId).toBe('student-1');
  });
});
