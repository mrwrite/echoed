import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { Subscription } from 'rxjs';

import { EchoConfirmationDialogComponent } from '../../components/echo-confirmation-dialog/echo-confirmation-dialog.component';
import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { User } from '../../models/user';
import { PermissionsService } from '../../services/permissions.service';
import { UsersService } from '../../services/users.service';

@Component({
  selector: 'admin-users-page',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, EchoConfirmationDialogComponent, EchoLoadingStateComponent, EchoStatePanelComponent],
  templateUrl: './admin-users.component.html',
  styleUrl: './admin-users.component.scss'
})
export class AdminUsersComponent implements OnInit, OnDestroy {
  users: User[] = [];
  search = '';
  roleFilter = 'all';
  loading = true;
  loadFailed = false;
  currentUserId = '';
  pendingDelete?: User;
  deleting = false;
  deleteError = '';
  private readonly subscriptions = new Subscription();

  constructor(private readonly usersService: UsersService, permissions: PermissionsService) {
    this.subscriptions.add(permissions.user$.subscribe(user => this.currentUserId = user?.user_id ?? ''));
  }

  ngOnInit(): void { this.loadUsers(); }
  ngOnDestroy(): void { this.subscriptions.unsubscribe(); }

  get roles(): string[] { return [...new Set(this.users.map(user => user.role))].sort(); }
  get filteredUsers(): User[] {
    const query = this.search.trim().toLowerCase();
    return this.users.filter(user => {
      const name = `${user.firstname} ${user.lastname}`.toLowerCase();
      return (!query || name.includes(query)) && (this.roleFilter === 'all' || user.role === this.roleFilter);
    });
  }

  loadUsers(): void {
    this.loading = true;
    this.loadFailed = false;
    this.subscriptions.add(this.usersService.getUsers().subscribe({
      next: users => { this.users = users; this.loading = false; },
      error: () => { this.loadFailed = true; this.loading = false; },
    }));
  }

  requestDelete(user: User): void {
    if (user.id === this.currentUserId) return;
    this.deleteError = '';
    this.pendingDelete = user;
  }

  cancelDelete(): void { if (!this.deleting) this.pendingDelete = undefined; }

  confirmDelete(): void {
    if (!this.pendingDelete || this.deleting) return;
    const user = this.pendingDelete;
    this.deleting = true;
    this.deleteError = '';
    this.subscriptions.add(this.usersService.deleteUser(user.id).subscribe({
      next: () => {
        this.users = this.users.filter(item => item.id !== user.id);
        this.deleting = false;
        this.pendingDelete = undefined;
      },
      error: () => {
        this.deleting = false;
        this.deleteError = 'The user was not deleted. No local changes were made.';
      },
    }));
  }

  displayName(user: User): string { return `${user.firstname} ${user.lastname}`.trim() || 'Unnamed user'; }
  roleLabel(role: string): string { return role.replace(/_/g, ' '); }
}
