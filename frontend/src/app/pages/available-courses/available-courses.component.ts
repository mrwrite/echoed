import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CoursesService } from '../../services/courses.service';
import { StudentCourseWithDetails } from '../../models/student-course-with-details.model';
import { Course } from '../../models/course';
import { StudentCourseCardComponent } from '../../components/student-course-card/student-course-card.component';
import { EchoButtonComponent } from '../../components/echo-button/echo-button.component';
import { ToastService } from '../../services/toast.service';

@Component({
  selector: 'available-courses-page',
  standalone: true,
  imports: [CommonModule, StudentCourseCardComponent, EchoButtonComponent],
  templateUrl: './available-courses.component.html',
  styleUrl: './available-courses.component.scss'
})
export class AvailableCoursesComponent implements OnInit {
  availableCourses: Course[] = [];
  studentCourses: StudentCourseWithDetails[] = [];

  constructor(
    private coursesService: CoursesService,
    private toastService: ToastService
  ) {}

  ngOnInit(): void {
    this.loadStudentCourses();
  }

  loadStudentCourses(): void {
    this.coursesService.getStudentCourses().subscribe({
      next: courses => {
        this.studentCourses = courses;
        this.loadAvailableCourses();
      },
      error: err => {
        console.error('Failed to load student courses', err);
      }
    });
  }

  loadAvailableCourses(): void {
    this.coursesService.getCourses().subscribe({
      next: courses => {
        const enrolledCourseIds = this.studentCourses.map(sc => sc.course_id);
        this.availableCourses = courses.filter(c => !enrolledCourseIds.includes(c.id));
      },
      error: err => {
        console.error('Failed to load available courses', err);
      }
    });
  }

  enrollInCourse(courseId: string): void {
    this.coursesService.enrollInCourse(courseId).subscribe({
      next: () => {
        this.toastService.show('Enrollment successful!', 'success');
        this.loadStudentCourses();
      },
      error: err => {
        console.error('Enrollment failed', err);
        this.toastService.show('Enrollment failed. You may already be enrolled.', 'error');
      }
    });
  }
}
