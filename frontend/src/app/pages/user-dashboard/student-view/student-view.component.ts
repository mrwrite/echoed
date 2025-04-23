import { Component, Input } from '@angular/core';
import { UserInfo } from '../../../models/user-info';

@Component({
  selector: 'echoed-student-view',
  standalone: true,
  imports: [],
  templateUrl: './student-view.component.html',
  styleUrl: './student-view.component.scss'
})
export class StudentViewComponent {
  @Input() userInfo!: UserInfo;
}
