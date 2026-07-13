import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { of, throwError } from 'rxjs';

import { AdminUsersComponent } from './admin-users.component';
import { UsersService } from '../../services/users.service';
import { PermissionsService } from '../../services/permissions.service';

describe('AdminUsersComponent', () => {
  let fixture: ComponentFixture<AdminUsersComponent>;
  const usersService = jasmine.createSpyObj('UsersService', ['getUsers', 'deleteUser']);

  beforeEach(async () => {
    usersService.getUsers.and.returnValue(of([
      { id: '1', firstname: 'Ada', lastname: 'Lovelace', username: 'ada', email: 'ada@example.test', hashed_password: 'secret', role: 'student', created_at: new Date() },
      { id: '2', firstname: 'Grace', lastname: 'Hopper', username: 'grace', email: 'grace@example.test', role: 'admin', created_at: new Date() },
    ]));
    await TestBed.configureTestingModule({ imports: [RouterTestingModule, AdminUsersComponent], providers: [
      { provide: UsersService, useValue: usersService }, { provide: PermissionsService, useValue: { user$: of({ user_id: '2' }) } },
    ] }).compileComponents();
    fixture = TestBed.createComponent(AdminUsersComponent);
  });

  it('omits contact and authentication fields from the broad user list', () => {
    fixture.detectChanges(); const text = fixture.nativeElement.textContent;
    expect(text).toContain('Ada Lovelace'); expect(text).not.toContain('ada@example.test'); expect(text).not.toContain('secret');
  });

  it('filters by name and role with an announced result count', () => {
    fixture.detectChanges(); fixture.componentInstance.search = 'Ada'; fixture.componentInstance.roleFilter = 'student'; fixture.detectChanges();
    expect(fixture.componentInstance.filteredUsers.length).toBe(1);
    expect(fixture.nativeElement.textContent).toContain('1 user shown');
  });

  it('renders a retryable load failure', () => {
    usersService.getUsers.and.returnValue(throwError(() => new Error('failed')));
    fixture.componentInstance.loadUsers(); fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Users could not be loaded');
  });
});
