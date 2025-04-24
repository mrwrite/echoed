import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UserInfo } from '../../../models/user-info';
import { UsersService } from '../../../services/users.service';
import { User } from '../../../models/user';

@Component({
  selector: 'echoed-admin-view',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './admin-view.component.html',
  styleUrl: './admin-view.component.scss'
})
export class AdminViewComponent {
  @Input() userInfo!: UserInfo;
  users: User[] = [];
  studentCount: number = 0;
  teacherCount: number = 0;

  constructor(private usersService: UsersService) { }

  ngOnInit() {
    this.usersService.getUsers().subscribe((users: User[]) => {
      this.users = users;
      this.studentCount = this.users.filter(user => user.role === 'student').length;
      this.teacherCount = this.users.filter(user => user.role === 'teacher').length;
    });
  }

}
