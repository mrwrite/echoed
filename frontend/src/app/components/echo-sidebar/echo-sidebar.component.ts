import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UserInfo } from '../../models/user-info';
import { RoleService } from '../../services/role.service';
import { IconModule } from '../../shared/icon/icon.module';

@Component({
  selector: 'echo-sidebar',
  standalone: true,
  imports: [CommonModule, IconModule],
  styleUrls: ['./echo-sidebar.component.scss'],
  templateUrl: './echo-sidebar.component.html',
})
export class SidebarComponent {
  @Input() collapsed = false;
  @Input() userInfo!: UserInfo;
  @Output() toggle = new EventEmitter<void>();

  constructor(public roleService: RoleService) {}
}
