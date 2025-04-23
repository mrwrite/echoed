import { Component, Input } from '@angular/core';
import { UserInfo } from '../../../models/user-info';

@Component({
  selector: 'echoed-admin-view',
  standalone: true,
  imports: [],
  templateUrl: './admin-view.component.html',
  styleUrl: './admin-view.component.scss'
})
export class AdminViewComponent {
  @Input() userInfo!: UserInfo;
}
