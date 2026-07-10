import { Component, EventEmitter, Input, Output, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { combineLatest, map } from 'rxjs';
import { UserInfo } from '../../models/user-info';
import { IconModule } from '../../shared/icon/icon.module';
import { PermissionsService } from '../../services/permissions.service';
import { EchoLoadingStateComponent } from '../echo-loading-state/echo-loading-state.component';
import { ShellNavigationService } from '../../services/shell-navigation.service';

@Component({
  selector: 'echo-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule, IconModule, EchoLoadingStateComponent],
  styleUrls: ['./echo-sidebar.component.scss'],
  templateUrl: './echo-sidebar.component.html',
})
export class SidebarComponent {
  @Input() collapsed = false;
  @Input() mobileMode = false;
  @Input() userInfo!: UserInfo;
  @Output() toggle = new EventEmitter<void>();

  private readonly permissionsService = inject(PermissionsService);
  private readonly shellNavigation = inject(ShellNavigationService);

  readonly ready$ = this.permissionsService.ready$;
  readonly visibleNavSections$ = combineLatest([
    this.permissionsService.user$,
    this.permissionsService.permissions$
  ]).pipe(
    // Recompute section arrays from observables so OnPush/async pipe views
    // update as soon as permissions resolve (no click/manual detect needed).
    map(([, permissions]) => this.shellNavigation.visibleSections(permissions))
  );

  readonly primarySpace$ = this.permissionsService.permissions$.pipe(
    map((permissions) => this.shellNavigation.getPrimarySpace(permissions))
  );
}
