import { ComponentFixture, TestBed } from '@angular/core/testing';
import { convertToParamMap, Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { of, throwError } from 'rxjs';

import { AdminUserDetailComponent } from './admin-user-detail.component';
import { UsersService } from '../../services/users.service';
import { PermissionsService } from '../../services/permissions.service';
import { ActivatedRoute } from '@angular/router';

describe('AdminUserDetailComponent', () => {
  let fixture: ComponentFixture<AdminUserDetailComponent>;
  const user = { id: 'user-1', firstname: 'Ada', lastname: 'Lovelace', username: 'ada', email: 'ada@example.test', role: 'student', created_at: new Date() };
  const users = jasmine.createSpyObj('UsersService', ['getUser', 'updateUserRole', 'deleteUser']);

  beforeEach(async () => {
    users.getUser.calls.reset();
    users.updateUserRole.calls.reset();
    users.deleteUser.calls.reset();
    users.getUser.and.returnValue(of(user)); users.updateUserRole.and.returnValue(of({ message: 'ok' })); users.deleteUser.and.returnValue(of({}));
    await TestBed.configureTestingModule({ imports: [RouterTestingModule, AdminUserDetailComponent], providers: [
      { provide: UsersService, useValue: users }, { provide: PermissionsService, useValue: { user$: of({ user_id: 'admin-1' }) } },
      { provide: ActivatedRoute, useValue: { snapshot: { paramMap: convertToParamMap({ userId: 'user-1' }) } } },
    ] }).compileComponents();
    fixture = TestBed.createComponent(AdminUserDetailComponent); fixture.detectChanges();
  });

  it('requires confirmation before applying a supported role change', () => {
    fixture.componentInstance.selectedRole = 'teacher'; fixture.componentInstance.requestRoleChange();
    expect(fixture.componentInstance.confirmRole).toBeTrue(); expect(users.updateUserRole).not.toHaveBeenCalled();
    fixture.componentInstance.applyRoleChange();
    expect(users.updateUserRole).toHaveBeenCalledWith(user, 'teacher'); expect(fixture.componentInstance.user?.role).toBe('teacher');
  });

  it('keeps the displayed role unchanged after an API failure', () => {
    users.updateUserRole.and.returnValue(throwError(() => new Error('failed')));
    fixture.componentInstance.selectedRole = 'admin'; fixture.componentInstance.requestRoleChange(); fixture.componentInstance.applyRoleChange();
    expect(fixture.componentInstance.user?.role).toBe('student'); expect(fixture.componentInstance.actionError).toContain('not changed');
  });
});
