import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { Subscription } from 'rxjs';

import { EchoConfirmationDialogComponent } from '../../components/echo-confirmation-dialog/echo-confirmation-dialog.component';
import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { Course } from '../../models/course';
import { CourseGovernanceSummary } from '../../models/course-publish-readiness.model';
import { CoursesService } from '../../services/courses.service';

@Component({
  selector: 'admin-courses-page',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, EchoConfirmationDialogComponent, EchoLoadingStateComponent, EchoStatePanelComponent],
  templateUrl: './admin-courses.component.html',
  styleUrl: './admin-courses.component.scss'
})
export class AdminCoursesComponent implements OnInit, OnDestroy {
  courses: Course[] = [];
  selected?: Course;
  governance?: CourseGovernanceSummary;
  detailMode = false;
  search = '';
  loading = true;
  failed = false;
  governanceFailed = false;
  pendingDelete?: Course;
  deleting = false;
  deleteError = '';
  private readonly subscriptions = new Subscription();

  constructor(private readonly coursesService: CoursesService, private readonly route: ActivatedRoute, private readonly router: Router) {}
  ngOnInit(): void { this.detailMode = this.route.snapshot.paramMap.has('courseId'); this.load(); }
  ngOnDestroy(): void { this.subscriptions.unsubscribe(); }
  get filteredCourses(): Course[] { const q = this.search.trim().toLowerCase(); return this.courses.filter(course => !q || course.title.toLowerCase().includes(q)); }

  load(): void {
    this.loading = true; this.failed = false;
    const id = this.route.snapshot.paramMap.get('courseId');
    if (id) {
      this.subscriptions.add(this.coursesService.getCourseById(id).subscribe({ next: course => { this.selected = course as unknown as Course; this.loading = false; this.loadGovernance(id); }, error: () => { this.failed = true; this.loading = false; } }));
      return;
    }
    this.subscriptions.add(this.coursesService.getCourses().subscribe({ next: courses => { this.courses = courses; this.loading = false; }, error: () => { this.failed = true; this.loading = false; } }));
  }

  loadGovernance(courseId: string): void {
    this.governanceFailed = false;
    this.subscriptions.add(this.coursesService.getCourseGovernanceSummary(courseId).subscribe({ next: value => this.governance = value, error: () => this.governanceFailed = true }));
  }

  requestDelete(course: Course): void { this.deleteError = ''; this.pendingDelete = course; }
  cancelDelete(): void { if (!this.deleting) this.pendingDelete = undefined; }
  confirmDelete(): void {
    if (!this.pendingDelete || this.deleting) return;
    const course = this.pendingDelete; this.deleting = true; this.deleteError = '';
    this.subscriptions.add(this.coursesService.deleteCourse(course.id).subscribe({
      next: () => { this.deleting = false; this.pendingDelete = undefined; this.router.navigate(['/admin/courses']); },
      error: () => { this.deleting = false; this.deleteError = 'The course was not deleted. No local changes were made.'; },
    }));
  }

  status(course: Course): string { return course.revision_status || (course.published_at ? 'published' : 'status unavailable'); }
  label(value: string): string { return value.replace(/_/g, ' '); }
}
