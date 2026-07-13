import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { Subscription } from 'rxjs';

import { EchoConfirmationDialogComponent } from '../../components/echo-confirmation-dialog/echo-confirmation-dialog.component';
import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { User } from '../../models/user';
import { PermissionsService } from '../../services/permissions.service';
import { UsersService } from '../../services/users.service';

@Component({
  selector: 'app-admin-user-detail',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, EchoConfirmationDialogComponent, EchoLoadingStateComponent, EchoStatePanelComponent],
  templateUrl: './admin-user-detail.component.html',
  styleUrl: './admin-user-detail.component.scss',
})
export class AdminUserDetailComponent implements OnInit, OnDestroy {
  readonly assignableRoles = ['student', 'teacher', 'admin'];
  user?: User;
  selectedRole = '';
  currentUserId = '';
  loading = true;
  failed = false;
  saving = false;
  deleting = false;
  confirmRole = false;
  confirmDelete = false;
  actionError = '';
  successMessage = '';
  private readonly subscriptions = new Subscription();

  constructor(
    private readonly route: ActivatedRoute,
    readonly router: Router,
    private readonly users: UsersService,
    permissions: PermissionsService,
  ) { this.subscriptions.add(permissions.user$.subscribe(user => this.currentUserId = user?.user_id ?? '')); }

  ngOnInit(): void { this.load(); }
  ngOnDestroy(): void { this.subscriptions.unsubscribe(); }
  get isSelf(): boolean { return this.user?.id === this.currentUserId; }
  get displayName(): string { return this.user ? `${this.user.firstname} ${this.user.lastname}`.trim() || 'Unnamed user' : ''; }

  load(): void {
    const id = this.route.snapshot.paramMap.get('userId');
    if (!id) { this.loading = false; this.failed = true; return; }
    this.loading = true; this.failed = false;
    this.subscriptions.add(this.users.getUser(id).subscribe({
      next: user => { this.user = user; this.selectedRole = user.role; this.loading = false; },
      error: () => { this.failed = true; this.loading = false; },
    }));
  }

  requestRoleChange(): void {
    if (!this.user || this.isSelf || this.selectedRole === this.user.role || !this.assignableRoles.includes(this.selectedRole)) return;
    this.actionError = ''; this.confirmRole = true;
  }

  applyRoleChange(): void {
    if (!this.user || this.saving) return;
    this.saving = true; this.actionError = '';
    this.subscriptions.add(this.users.updateUserRole(this.user, this.selectedRole).subscribe({
      next: () => {
        if (this.user) this.user = { ...this.user, role: this.selectedRole };
        this.saving = false; this.confirmRole = false;
        this.successMessage = `Role updated to ${this.roleLabel(this.selectedRole)}.`;
      },
      error: () => { this.saving = false; this.actionError = 'The role was not changed. Review the account and try again.'; },
    }));
  }

  deleteUser(): void {
    if (!this.user || this.isSelf || this.deleting) return;
    this.deleting = true; this.actionError = '';
    this.subscriptions.add(this.users.deleteUser(this.user.id).subscribe({
      next: () => this.router.navigate(['/admin/users']),
      error: () => { this.deleting = false; this.actionError = 'The user was not deleted. No local changes were made.'; },
    }));
  }

  roleLabel(role: string): string { return role.replace(/_/g, ' '); }
}
