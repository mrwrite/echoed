import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { OrganizationMember } from '../../models/organization';
import { OrganizationService } from '../../services/organization.service';

type PeopleMode = 'members' | 'teachers' | 'students';

@Component({
  selector: 'app-organization-people',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, EchoLoadingStateComponent, EchoStatePanelComponent],
  templateUrl: './organization-people.component.html',
  styleUrl: './organization-people.component.scss',
})
export class OrganizationPeopleComponent implements OnInit {
  mode: PeopleMode = 'members';
  members: OrganizationMember[] = [];
  searchTerm = '';
  roleFilter = '';
  statusFilter = '';
  loading = true;
  loadError = '';

  constructor(private readonly route: ActivatedRoute, private readonly organizations: OrganizationService) {}

  ngOnInit(): void {
    this.mode = (this.route.snapshot.data['mode'] as PeopleMode) || 'members';
    this.load();
  }

  get title(): string {
    return this.mode === 'teachers' ? 'Teachers' : this.mode === 'students' ? 'Students' : 'Members';
  }

  get intro(): string {
    if (this.mode === 'teachers') return 'Review teachers and instructors who belong to the active organization.';
    if (this.mode === 'students') return 'Review learner memberships without exposing progress or profile details.';
    return 'Review the people and organization roles present in the active organization.';
  }

  get availableRoles(): string[] {
    return [...new Set(this.members.map(member => member.role))].sort();
  }

  get filteredMembers(): OrganizationMember[] {
    const search = this.searchTerm.trim().toLowerCase();
    return this.members.filter(member => {
      if (this.mode === 'teachers' && !['teacher', 'instructor'].includes(member.role)) return false;
      if (this.mode === 'students' && member.role !== 'student') return false;
      if (this.roleFilter && member.role !== this.roleFilter) return false;
      if (this.statusFilter && member.status !== this.statusFilter) return false;
      return !search || member.display_name.toLowerCase().includes(search) || member.username.toLowerCase().includes(search);
    });
  }

  load(): void {
    const orgId = this.organizations.getActiveOrgId();
    this.loading = true;
    this.loadError = '';
    if (!orgId) {
      this.loading = false;
      this.loadError = 'Choose an active organization before reviewing members.';
      return;
    }
    this.organizations.getMembers(orgId).subscribe({
      next: members => {
        this.members = members;
        this.loading = false;
      },
      error: () => {
        this.members = [];
        this.loading = false;
        this.loadError = 'We could not load organization members. No membership data was changed.';
      },
    });
  }

  label(value: string): string {
    return value.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
  }
}
