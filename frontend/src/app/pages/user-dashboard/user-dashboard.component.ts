import { Component, Input, OnInit } from '@angular/core';
import { AuthService } from '../../services/auth.service'
import { UserInfo } from '../../models/user-info';
import { AdminViewComponent } from './admin-view/admin-view.component';
import { CommonModule } from '@angular/common';
import { StudentViewComponent } from "./student-view/student-view.component";
import  { TeacherViewComponent } from './teacher-view/teacher-view.component';

@Component({
  selector: 'user-dashboard',
  standalone: true,
  imports: [CommonModule, AdminViewComponent, StudentViewComponent, TeacherViewComponent],
  templateUrl: './user-dashboard.component.html',
  styleUrl: './user-dashboard.component.scss'
})
export class UserDashboardComponent implements OnInit {
  userRole: string = 'student'; 
  @Input() userInfo!: UserInfo; 

  constructor(private authService: AuthService) { }

  ngOnInit(): void {    
    console.log(this.userInfo);
  }
  

}
