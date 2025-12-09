import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { UserInfo } from '../../../models/user-info';
import { CoursesService } from '../../../services/courses.service';
import { Course } from '../../../models/course';
import { IconModule } from '../../../shared/icon/icon.module';
import { ToastService } from '../../../services/toast.service';

@Component({
  selector: 'echoed-teacher-view',
  standalone: true,
  imports: [CommonModule, IconModule],
  templateUrl: './teacher-view.component.html',
  styleUrl: './teacher-view.component.scss'
})
export class TeacherViewComponent implements OnInit {
  @Input() userInfo!: UserInfo;

  courses: Course[] = [];
  readonly visibleCount = 5;

  constructor(private coursesService: CoursesService, private router: Router, private toastService: ToastService) {}

  ngOnInit(): void {
    this.coursesService.getCourses().subscribe(courses => {
      this.courses = courses;
    });
  }

  get visibleCourses(): Course[] {
    return this.courses.slice(0, this.visibleCount);
  }

  onAddCourse() {
    this.router.navigate(['/home/courses/new']);
  }

  onManageCourse(courseId: string) {
    this.router.navigate(['/home/courses', courseId, 'edit']);
  }

  deleteCourse(courseId: string) {
    this.coursesService.deleteCourse(courseId).subscribe(() => {
      this.courses = this.courses.filter(c => c.id !== courseId);
    });
  }

  viewAllCourses() {
    this.router.navigate(['/home/admin/courses']);
  }

  assignCourse() {
    this.router.navigate(['/home/admin/courses']);
  }

  startLiveLesson() {
    const targetCourse = this.courses[0];
    if (targetCourse) {
      this.router.navigate(['/home/lesson', targetCourse.id || 'demo']);
    } else {
      this.toastService.show('Add a course first to start a live lesson.', 'info');
    }
  }

  viewReports() {
    this.router.navigate(['/home/admin/users']);
  }
}
