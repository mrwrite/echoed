import { Component, Input } from '@angular/core';
import { UserInfo } from '../../../models/user-info';

@Component({
  selector: 'echoed-teacher-view',
  standalone: true,
  imports: [],
  templateUrl: './teacher-view.component.html',
  styleUrl: './teacher-view.component.scss'
})
export class TeacherViewComponent {
  @Input() userInfo!: UserInfo;
}
