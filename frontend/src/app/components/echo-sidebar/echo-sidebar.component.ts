import { Component, EventEmitter, Input, Output, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { combineLatest, map } from 'rxjs';
import { UserInfo } from '../../models/user-info';
import { IconModule } from '../../shared/icon/icon.module';
import { PermissionsService } from '../../services/permissions.service';
import { EchoLoadingStateComponent } from '../echo-loading-state/echo-loading-state.component';

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
  imports: [CommonModule, RouterModule, IconModule, EchoLoadingStateComponent],
  styleUrls: ['./echo-sidebar.component.scss'],
  templateUrl: './echo-sidebar.component.html',
})
export class SidebarComponent {
  @Input() collapsed = false;
  @Input() userInfo!: UserInfo;
  @Output() toggle = new EventEmitter<void>();

  private readonly navSections: NavSection[] = [
    {
      title: 'Workspace',
      items: [
        { label: 'Workspace', route: '/workspace', icon: 'Home', permission: 'nav:workspace' },
        { label: 'Projects', route: '/workspace/projects', icon: 'ClipboardList', permission: 'nav:projects' },
        { label: 'Product Studio', route: '/workspace/product-studio', icon: 'BookOpen', permission: 'nav:product-studio' },
        { label: 'Products', route: '/workspace/products', icon: 'Book', permission: 'nav:products' },
      ]
    },
    {
      title: 'Knowledge Ops',
      items: [
        { label: 'Knowledge Sources', route: '/workspace/knowledge-sources', icon: 'BookOpen', permission: 'nav:knowledge-sources' },
        { label: 'Artifacts', route: '/workspace/artifacts', icon: 'Award', permission: 'nav:artifacts' },
        { label: 'Review Center', route: '/workspace/review-center', icon: 'ClipboardList', permission: 'nav:review-center' },
        { label: 'Access', route: '/workspace/access', icon: 'Users', permission: 'nav:access' },
        { label: 'Analytics', route: '/workspace/analytics', icon: 'SlidersHorizontal', permission: 'nav:analytics' },
        { label: 'Commercial', route: '/workspace/commercial', icon: 'SlidersHorizontal', permission: 'nav:commercial' },
      ]
    },
    {
      title: 'People & Settings',
      items: [
        { label: 'Learners', route: '/workspace/learners', icon: 'User', permission: 'nav:learners' },
        { label: 'Cohorts', route: '/workspace/learners/cohorts', icon: 'Users', permission: 'nav:cohorts' },
        { label: 'Settings', route: '/workspace/settings', icon: 'SlidersHorizontal', permission: 'nav:settings' },
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
