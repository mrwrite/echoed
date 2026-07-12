import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { Course } from '../../models/course';
import { CoursesService } from '../../services/courses.service';

@Component({
  selector: 'app-teacher-curriculum',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, EchoLoadingStateComponent, EchoStatePanelComponent],
  template: `
    <section class="teacher-curriculum" aria-labelledby="teacher-curriculum-title">
      <header class="teacher-curriculum__header">
        <div>
          <p class="teacher-curriculum__eyebrow">Teach</p>
          <h1 id="teacher-curriculum-title">Browse curriculum</h1>
          <p>Find courses, preview the learner path, and choose learning to assign from existing course data.</p>
        </div>
        <a routerLink="/teach/classes">My classes</a>
      </header>

      <section class="teacher-curriculum__panel" aria-labelledby="curriculum-filter-title">
        <div>
          <p class="teacher-curriculum__eyebrow">Filter</p>
          <h2 id="curriculum-filter-title">Search available courses</h2>
        </div>
        <label>
          <span>Search courses</span>
          <input [(ngModel)]="searchTerm" type="search" placeholder="Search title, description, or objective" />
        </label>
      </section>

      <app-echo-loading-state
        *ngIf="loading"
        density="page"
        ariaLabel="teacher-curriculum-loading"
        title="Loading curriculum"
        body="We are loading the existing course catalog."
      ></app-echo-loading-state>
      <app-echo-state-panel
        *ngIf="!loading && loadError"
        variant="error"
        eyebrow="Curriculum unavailable"
        title="We could not load courses"
        [body]="loadError"
        actionLabel="Retry"
        (action)="loadCourses()"
      ></app-echo-state-panel>
      <app-echo-state-panel
        *ngIf="!loading && !loadError && courses.length === 0"
        variant="empty"
        eyebrow="No curriculum"
        title="No courses are available"
        body="Courses from the existing course API will appear here when available."
      ></app-echo-state-panel>
      <app-echo-state-panel
        *ngIf="!loading && !loadError && courses.length > 0 && filteredCourses.length === 0"
        variant="empty"
        eyebrow="No matching courses"
        title="No course matches your search"
        body="Clear the search to return to the full curriculum list."
      ></app-echo-state-panel>

      <div *ngIf="!loading && !loadError && filteredCourses.length > 0" class="teacher-curriculum__grid">
        <article *ngFor="let course of filteredCourses" class="teacher-curriculum__card">
          <p class="teacher-curriculum__eyebrow">Course</p>
          <h2>{{ course.title }}</h2>
          <p>{{ course.description || 'No description available.' }}</p>
          <dl>
            <div>
              <dt>Units</dt>
              <dd>{{ course.units?.length || 0 }}</dd>
            </div>
            <div>
              <dt>Lessons</dt>
              <dd>{{ lessonCount(course) }}</dd>
            </div>
          </dl>
          <p *ngIf="course.learning_objectives" class="teacher-curriculum__objective">{{ course.learning_objectives }}</p>
          <div class="teacher-curriculum__actions">
            <a [routerLink]="['/teach/courses', course.id, 'preview']">Preview course</a>
            <a routerLink="/teach/assignments">Assign learning</a>
          </div>
        </article>
      </div>
    </section>
  `,
  styleUrl: './teacher-curriculum.component.scss',
})
export class TeacherCurriculumComponent implements OnInit {
  courses: Course[] = [];
  searchTerm = '';
  loading = true;
  loadError = '';

  constructor(private coursesService: CoursesService) {}

  ngOnInit(): void {
    this.loadCourses();
  }

  get filteredCourses(): Course[] {
    const search = this.searchTerm.trim().toLowerCase();
    if (!search) {
      return this.courses;
    }
    return this.courses.filter(course =>
      course.title.toLowerCase().includes(search) ||
      (course.description || '').toLowerCase().includes(search) ||
      (course.learning_objectives || '').toLowerCase().includes(search)
    );
  }

  loadCourses(): void {
    this.loading = true;
    this.loadError = '';
    this.coursesService.getCourses().subscribe({
      next: (courses) => {
        this.courses = courses;
        this.loading = false;
      },
      error: () => {
        this.courses = [];
        this.loading = false;
        this.loadError = 'We could not load curriculum. No course or learner progress was changed.';
      },
    });
  }

  lessonCount(course: Course): number {
    return (course.units || []).reduce((count, unit) => count + (unit.lessons?.length || 0), 0);
  }
}
