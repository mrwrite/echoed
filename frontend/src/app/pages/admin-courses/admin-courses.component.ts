import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CoursesService } from '../../services/courses.service';
import { Course } from '../../models/course';
import { Router } from '@angular/router';

@Component({
  selector: 'admin-courses-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './admin-courses.component.html',
  styleUrl: './admin-courses.component.scss'
})
export class AdminCoursesComponent implements OnInit {
  courses: Course[] = [];

  constructor(private coursesService: CoursesService, private router: Router) {}

  ngOnInit(): void {
    this.coursesService.getCourses().subscribe(courses => {
      this.courses = courses;
    });
  }

  onManageCourse(courseId: string) {
    this.router.navigate(['/home/courses', courseId, 'edit']);
  }
}
