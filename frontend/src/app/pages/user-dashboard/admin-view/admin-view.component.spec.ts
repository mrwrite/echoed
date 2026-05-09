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
    usageStatsService.usageResponse = new Subject<any[]>().asObservable();
    analyticsService.overviewResponse = new Subject<any>().asObservable();

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('[data-echo-loading="section"]')).not.toBeNull();
    expect(compiled.textContent).toContain('Loading platform overview');
    expect(compiled.textContent).toContain('Loading recent signups');
  });

  it('uses EchoStatePanel for admin empty states', () => {
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const emptyStates = compiled.querySelectorAll('[data-echo-state="empty"]');
    expect(emptyStates.length).toBeGreaterThan(0);
    expect(compiled.textContent).toContain('Recent user activity will appear here');
    expect(compiled.textContent).toContain('Usage statistics will appear here');
    expect(compiled.textContent).toContain('Course management will appear here');
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

    usersService.usersResponse = of([{ id: 'user-1', firstname: 'Grace', lastname: 'Hopper', role: 'admin', created_at: '2026-05-01T00:00:00.000Z' }]);
    coursesService.coursesResponse = of([{ id: 'course-1', title: 'Biology' }]);
    usageStatsService.usageResponse = of([{ label: 'Daily Active Users', value: 82, color: 'bg-primary' }]);
    analyticsService.overviewResponse = of({ totals: { students: 14, teachers: 2, courses: 5, pending_enrollments: 1 } });

    const buttons = Array.from(fixture.nativeElement.querySelectorAll('button')) as HTMLButtonElement[];
    buttons.filter((button) => button.textContent?.trim() === 'Retry').forEach((button) => button.click());
    fixture.detectChanges();

    expect(usersService.getUsers).toHaveBeenCalledTimes(2);
    expect(coursesService.getCourses).toHaveBeenCalledTimes(2);
    expect(usageStatsService.getUsageStats).toHaveBeenCalledTimes(2);
    expect(analyticsService.getAdminOverview).toHaveBeenCalledTimes(2);
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
});
