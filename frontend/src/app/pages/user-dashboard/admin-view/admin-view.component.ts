import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UserInfo } from '../../../models/user-info';
import { UsersService } from '../../../services/users.service';
import { CoursesService } from '../../../services/courses.service';
import { User } from '../../../models/user';
import { Course } from '../../../models/course';
import { IconModule } from '../../../shared/icon/icon.module';
import { Router } from '@angular/router';
import { StatCardComponent } from '../../../components/stat-card/stat-card.component';

interface Metric {
  icon: string;
  label: string;
  value: number | string;
}

@Component({
  selector: 'echoed-admin-view',
  standalone: true,
  imports: [CommonModule, IconModule, StatCardComponent],
  templateUrl: './admin-view.component.html',
  styleUrl: './admin-view.component.scss'
})
export class AdminViewComponent {
  @Input() userInfo!: UserInfo;
  users: User[] = [];
  courses: Course[] = [];

  studentCount = 0;
  teacherCount = 0;
  coursesCount = 0;
  metrics: Metric[] = [];

  constructor(
    private usersService: UsersService,
    private coursesService: CoursesService,
    private router: Router
  ) {}

  ngOnInit() {
    this.usersService.getUsers().subscribe((users: User[]) => {
      this.users = users;
      this.studentCount = this.users.filter(u => u.role === 'student').length;
      this.teacherCount = this.users.filter(u => u.role === 'teacher').length;
      this.updateMetrics();
    });

    this.coursesService.getCourses().subscribe(courses => {
      this.courses = courses;
      this.coursesCount = this.courses.length;
      this.updateMetrics();
    });

    // initialize metrics with default values
    this.updateMetrics();
  }

  private updateMetrics() {
    this.metrics = [
      { icon: 'User', label: 'Active Students', value: this.studentCount },
      { icon: 'User', label: 'Instructors', value: this.teacherCount },
      { icon: 'book-marked', label: 'Courses', value: this.coursesCount },
      { icon: 'clock', label: 'Pending Enrollments', value: 154 }
    ];
  }

  onAddCourse() {
    this.router.navigate(['/home/courses/new']);
  }

  onManageCourse(courseId: string) {
    this.router.navigate(['/home/courses', courseId, 'edit']);
  }
}
