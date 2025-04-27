import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UserInfo } from '../../../models/user-info';
import { UsersService } from '../../../services/users.service';
import { CoursesService } from '../../../services/courses.service';
import { User } from '../../../models/user';
import { Course } from '../../../models/course';
import { IconModule } from '../../../shared/icon/icon.module';
import { Router } from '@angular/router';

@Component({
  selector: 'echoed-admin-view',
  standalone: true,
  imports: [CommonModule, IconModule],
  templateUrl: './admin-view.component.html',
  styleUrl: './admin-view.component.scss'
})
export class AdminViewComponent {
  @Input() userInfo!: UserInfo;
  users: User[] = [];
  courses: Course[] = []; // Adjust the type according to your Course model
  studentCount: number = 0;
  teacherCount: number = 0;
  coursesCount: number = 0;

  constructor(private usersService: UsersService,
              private coursesService: CoursesService,
              private router: Router
  ) { }

  ngOnInit() {
    this.usersService.getUsers().subscribe((users: User[]) => {
      this.users = users;
      this.studentCount = this.users.filter(user => user.role === 'student').length;
      this.teacherCount = this.users.filter(user => user.role === 'teacher').length;
    });

    this.coursesService.getCourses().subscribe((courses) => {
      this.courses = courses;
      this.coursesCount = this.courses.length;
    });
  }

  onAddCourse() {
  
    this.router.navigate(['/home/courses/new']);
  }
  
  onManageCourse(courseId: string) {
    this.router.navigate(['/home/courses', courseId, 'edit']);
  }

}
