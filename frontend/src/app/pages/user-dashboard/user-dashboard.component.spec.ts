import { RouterTestingModule } from '@angular/router/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BehaviorSubject } from 'rxjs';

import { UserDashboardComponent } from './user-dashboard.component';
import { PermissionsService } from '../../services/permissions.service';
import { SharedUserService } from '../../services/shared-user.service';

class MockPermissionsService {
  readonly user$ = new BehaviorSubject<any>(null);
  readonly ready$ = new BehaviorSubject<boolean>(false);
}

class MockSharedUserService {
  setUserInfo = jasmine.createSpy('setUserInfo');
}

describe('UserDashboardComponent', () => {
  let component: UserDashboardComponent;
  let fixture: ComponentFixture<UserDashboardComponent>;
  let permissionsService: MockPermissionsService;
  let sharedUserService: MockSharedUserService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RouterTestingModule, UserDashboardComponent],
      providers: [
        { provide: PermissionsService, useClass: MockPermissionsService },
        { provide: SharedUserService, useClass: MockSharedUserService },
      ],
    })
    .compileComponents();

    fixture = TestBed.createComponent(UserDashboardComponent);
    component = fixture.componentInstance;
    permissionsService = TestBed.inject(PermissionsService) as unknown as MockPermissionsService;
    sharedUserService = TestBed.inject(SharedUserService) as unknown as MockSharedUserService;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('uses PermissionsService session state rather than raw token decode', () => {
    permissionsService.user$.next({ fullname: 'Teacher User', role: 'teacher' });
    permissionsService.ready$.next(true);
    fixture.detectChanges();

    expect(component.userInfo?.fullname).toBe('Teacher User');
    expect(component.userRole).toBe('teacher');
    expect(sharedUserService.setUserInfo).toHaveBeenCalledWith(jasmine.objectContaining({ fullname: 'Teacher User' }));
  });

  it('does not render role-specific content before readiness', () => {
    permissionsService.user$.next({ fullname: 'Teacher User', role: 'teacher' });
    permissionsService.ready$.next(false);
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('[aria-label="dashboard-loading"]')).not.toBeNull();
  });
});
