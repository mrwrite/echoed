import { Component, EventEmitter, Input, Output, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { combineLatest, map } from 'rxjs';
import { UserInfo } from '../../models/user-info';
import { IconModule } from '../../shared/icon/icon.module';
import { PermissionsService } from '../../services/permissions.service';

interface NavItem {
  label: string;
  route: string;
  icon: string;
  permission: string;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

@Component({
  selector: 'echo-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule, IconModule],
  styleUrls: ['./echo-sidebar.component.scss'],
  templateUrl: './echo-sidebar.component.html',
})
export class SidebarComponent {
  @Input() collapsed = false;
  @Input() userInfo!: UserInfo;
  @Output() toggle = new EventEmitter<void>();

  private readonly navSections: NavSection[] = [
    {
      title: 'Overview',
      items: [
        { label: 'Dashboard', route: '/home', icon: 'Home', permission: 'nav:dashboard' },
        { label: 'Courses', route: '/home/courses', icon: 'Book', permission: 'nav:courses' },
        { label: 'Programs', route: '/home/programs', icon: 'BookOpen', permission: 'nav:programs' },
        { label: 'Certifications', route: '/home/certifications', icon: 'Award', permission: 'nav:certifications' },
      ]
    },
    {
      title: 'Reports & Admin',
      items: [
        { label: 'Badges', route: '/home/admin/badges', icon: 'Award', permission: 'nav:admin-badges' },
        { label: 'Users', route: '/home/admin/users', icon: 'User', permission: 'nav:admin-users' },
        { label: 'Admin Courses', route: '/home/admin/courses', icon: 'ClipboardList', permission: 'nav:admin-courses' },
      ]
    },
    {
      title: 'Org & Studio',
      items: [
        { label: 'Invites', route: '/home/org/invites', icon: 'Mail', permission: 'nav:org-invites' },
        { label: 'Studio Courses', route: '/home/studio/courses', icon: 'BookOpen', permission: 'nav:studio-courses' },
        { label: 'Sections', route: '/home/sections', icon: 'Users', permission: 'nav:sections' },
        { label: 'Preferences', route: '/home/me/preferences', icon: 'SlidersHorizontal', permission: 'nav:preferences' },
      ]
    },
  ];

  private readonly permissionsService = inject(PermissionsService);

  readonly ready$ = this.permissionsService.ready$;
  readonly visibleNavSections$ = combineLatest([
    this.permissionsService.user$,
    this.permissionsService.permissions$
  ]).pipe(
    // Recompute section arrays from observables so OnPush/async pipe views
    // update as soon as permissions resolve (no click/manual detect needed).
    map(([, permissions]) => this.navSections
      .map(section => ({
        ...section,
        items: section.items.filter(item => permissions.has(item.permission))
      }))
      .filter(section => section.items.length > 0)
    )
  );

}
