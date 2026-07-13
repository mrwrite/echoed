import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UserInfo } from '../../../models/user-info';
import { AdminOverviewComponent } from '../../admin-overview/admin-overview.component';
import { StudentViewComponent } from '../student-view/student-view.component';
import { TeacherViewComponent } from '../teacher-view/teacher-view.component';
import { SharedUserService } from '../../../services/shared-user.service';

@Component({
  selector: 'echoed-role-selector',
  standalone: true,
  imports: [CommonModule, AdminOverviewComponent, StudentViewComponent, TeacherViewComponent],
  templateUrl: './echoed-role-selector.component.html',
  styleUrl: './echoed-role-selector.component.scss'
})
export class EchoedRoleSelectorComponent implements OnInit {
  userInfo: UserInfo | null = null;

  constructor(private sharedUserService: SharedUserService) { }

  ngOnInit(): void {
    this.userInfo = this.sharedUserService.getUserInfo(); // Get user info from shared service
  }
}
