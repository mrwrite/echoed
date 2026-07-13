import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { BehaviorSubject, of, throwError } from 'rxjs';

import { AdminOverviewComponent } from './admin-overview.component';
import { AnalyticsService } from '../../services/analytics.service';
import { UsersService } from '../../services/users.service';
import { CoursesService } from '../../services/courses.service';
import { OrganizationService } from '../../services/organization.service';
import { BadgesService } from '../../services/badges.service';
import { PermissionsService } from '../../services/permissions.service';

describe('AdminOverviewComponent', () => {
  let fixture: ComponentFixture<AdminOverviewComponent>;
  const analytics = jasmine.createSpyObj('AnalyticsService', ['getAdminOverview']);
  const users = jasmine.createSpyObj('UsersService', ['getUsers']);
  const courses = jasmine.createSpyObj('CoursesService', ['getCourses']);
  const organizations = jasmine.createSpyObj('OrganizationService', ['refreshOrganizations']);
  const badges = jasmine.createSpyObj('BadgesService', ['getBadges']);
  const role$ = new BehaviorSubject<any>({ role: 'admin', user_id: 'admin-1' });
  const permissions = { user$: role$.asObservable() };

  beforeEach(async () => {
    role$.next({ role: 'admin', user_id: 'admin-1' });
    analytics.getAdminOverview.calls.reset(); users.getUsers.calls.reset(); courses.getCourses.calls.reset();
    analytics.getAdminOverview.and.returnValue(of({ totals: { students: 2, teachers: 1, courses: 3, active_students: 2, total_enrollments: 2, pending_enrollments: 1 }, progress: { lessons_completed: 4, units_completed: 2, courses_completed: 1, course_completion_rate: 50 } }));
    users.getUsers.and.returnValue(of([{ id: '1' }, { id: '2' }]));
    courses.getCourses.and.returnValue(of([{ id: 'course-1' }]));
    organizations.refreshOrganizations.and.returnValue(of([{ id: 'org-1' }]));
    badges.getBadges.and.returnValue(of([{ id: 'badge-1' }]));
    await TestBed.configureTestingModule({ imports: [RouterTestingModule, AdminOverviewComponent], providers: [
      { provide: AnalyticsService, useValue: analytics }, { provide: UsersService, useValue: users },
      { provide: CoursesService, useValue: courses }, { provide: OrganizationService, useValue: organizations },
      { provide: BadgesService, useValue: badges }, { provide: PermissionsService, useValue: permissions },
    ] }).compileComponents();
  });

  it('renders supported counts and no invented attention queue', () => {
    fixture = TestBed.createComponent(AdminOverviewComponent); fixture.detectChanges();
    const text = fixture.nativeElement.textContent;
    expect(text).toContain('Total users'); expect(text).toContain('Organizations available to this account');
    expect(text).toContain('No verified platform attention queue is available');
  });

  it('keeps successful data visible after a partial API failure', () => {
    users.getUsers.and.returnValue(throwError(() => new Error('failed')));
    fixture = TestBed.createComponent(AdminOverviewComponent); fixture.detectChanges();
    const text = fixture.nativeElement.textContent;
    expect(text).toContain('Some platform information could not be loaded');
    expect(text).toContain('Courses');
  });

  it('shows compatible super-admin limitations without calling admin-only APIs', () => {
    role$.next({ role: 'super_admin', user_id: 'super-1' });
    fixture = TestBed.createComponent(AdminOverviewComponent); fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Limited super-admin compatibility');
    expect(analytics.getAdminOverview).not.toHaveBeenCalled(); expect(users.getUsers).not.toHaveBeenCalled(); expect(courses.getCourses).not.toHaveBeenCalled();
  });
});
