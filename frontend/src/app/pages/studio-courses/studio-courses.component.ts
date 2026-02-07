import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CoursesService } from '../../services/courses.service';
import { Course } from '../../models/course';
import { ToastService } from '../../services/toast.service';

@Component({
  selector: 'app-studio-courses',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './studio-courses.component.html',
  styleUrl: './studio-courses.component.scss'
})
export class StudioCoursesComponent implements OnInit {
  courses: Course[] = [];
  title = '';
  description = '';

  constructor(private coursesService: CoursesService, private toastService: ToastService) {}

  ngOnInit(): void {
    this.coursesService.getCourses().subscribe(courses => {
      this.courses = courses;
    });
  }

  createCourse(): void {
    if (!this.title || !this.description) {
      return;
    }
    this.coursesService.createCourse({ title: this.title, description: this.description, units: [] }).subscribe(() => {
      this.toastService.show('Draft course created.', 'success');
      this.coursesService.getCourses().subscribe(courses => {
        this.courses = courses;
        this.title = '';
        this.description = '';
      });
    });
  }
}
