import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CoursesService } from '../../services/courses.service';
import { Course } from '../../models/course';
import { Router, RouterLink } from '@angular/router';
import { CourseAuthoringCapabilities } from '../../models/course-authoring.model';

@Component({
  selector: 'app-studio-courses',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './studio-courses.component.html',
  styleUrl: './studio-courses.component.scss'
})
export class StudioCoursesComponent implements OnInit {
  courses: Course[] = [];
  capabilities?: CourseAuthoringCapabilities;
  loadFailed = false;

  constructor(
    private coursesService: CoursesService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.coursesService.getCourses().subscribe(courses => {
      this.courses = courses;
    });
    this.coursesService.getAuthoringCapabilities().subscribe({
      next: response => this.capabilities = response.capabilities,
      error: () => this.loadFailed = true,
    });
  }

  createCourse(): void {
    this.router.navigate(['/workspace/product-studio/courses/new']);
  }

  duplicateCourse(course: Course): void {
    const title = prompt('Title for the duplicated course:', `${course.title} (copy)`);
    if (!title?.trim()) return;
    const key = globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`;
    this.coursesService.duplicateAuthoringCourse(course.id, title.trim(), key).subscribe(copy => {
      void this.router.navigate(['/workspace/product-studio/courses', copy.id]);
    });
  }
}
