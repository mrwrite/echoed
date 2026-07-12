import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { forkJoin, of } from 'rxjs';
import { catchError, finalize } from 'rxjs/operators';

import { EchoConfirmationDialogComponent } from '../../components/echo-confirmation-dialog/echo-confirmation-dialog.component';
import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { Course } from '../../models/course';
import { Assignment, Enrollment, Section, SectionSummary } from '../../models/section';
import { User } from '../../models/user';
import { CoursesService } from '../../services/courses.service';
import { SectionsService } from '../../services/sections.service';
import { ToastService } from '../../services/toast.service';
import { UsersService } from '../../services/users.service';

type ClassTab = 'overview' | 'roster' | 'assignments' | 'progress' | 'discussion';

@Component({
  selector: 'app-section-detail',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
    EchoConfirmationDialogComponent,
    EchoLoadingStateComponent,
    EchoStatePanelComponent,
  ],
  templateUrl: './section-detail.component.html',
  styleUrl: './section-detail.component.scss'
})
export class SectionDetailComponent implements OnInit {
  sectionId = '';
  section?: Section;
  assignments: Assignment[] = [];
  roster: Enrollment[] = [];
  students: User[] = [];
  courses: Course[] = [];
  summary?: SectionSummary;
  activeTab: ClassTab = 'overview';
  targetType = 'lesson';
  targetId = '';
  dueAt = '';
  instructions = '';
  loading = true;
  savingAssignment = false;
  loadError = '';
  assignmentError = '';
  confirmationOpen = false;

  readonly tabs: { id: ClassTab; label: string }[] = [
    { id: 'overview', label: 'Overview' },
    { id: 'roster', label: 'Roster' },
    { id: 'assignments', label: 'Assignments' },
    { id: 'progress', label: 'Progress' },
    { id: 'discussion', label: 'Discussion' },
  ];

  constructor(
    private route: ActivatedRoute,
    private sectionsService: SectionsService,
    private coursesService: CoursesService,
    private usersService: UsersService,
    private toastService: ToastService
  ) {}

  ngOnInit(): void {
    this.sectionId = this.route.snapshot.paramMap.get('id') || '';
    this.loadClass();
  }

  get className(): string {
    return this.section?.name || 'Class detail';
  }

  get rosterCount(): number {
    return this.summary?.totals.enrolled ?? this.roster.length;
  }

  get completedLessons(): number {
    return this.summary?.totals.lessons_completed ?? 0;
  }

  get completedUnits(): number {
    return this.summary?.totals.units_completed ?? 0;
  }

  get upcomingAssignments(): Assignment[] {
    return [...this.assignments].sort((left, right) => {
      const leftDate = left.due_at ? new Date(left.due_at).getTime() : Number.MAX_SAFE_INTEGER;
      const rightDate = right.due_at ? new Date(right.due_at).getTime() : Number.MAX_SAFE_INTEGER;
      return leftDate - rightDate;
    });
  }

  loadClass(): void {
    if (!this.sectionId) {
      this.loading = false;
      this.loadError = 'This class link is missing a section id.';
      return;
    }

    this.loading = true;
    this.loadError = '';
    forkJoin({
      sections: this.sectionsService.listSections(),
      assignments: this.sectionsService.getAssignments(this.sectionId).pipe(catchError(() => of([] as Assignment[]))),
      roster: this.sectionsService.getRoster(this.sectionId).pipe(catchError(() => of([] as Enrollment[]))),
      summary: this.sectionsService.getSectionSummary(this.sectionId).pipe(catchError(() => of(undefined))),
      students: this.usersService.getStudents().pipe(catchError(() => of([] as User[]))),
      courses: this.coursesService.getCourses().pipe(catchError(() => of([] as Course[]))),
    }).subscribe({
      next: ({ sections, assignments, roster, summary, students, courses }) => {
        this.section = sections.find(section => section.id === this.sectionId);
        this.assignments = assignments;
        this.roster = roster;
        this.summary = summary;
        this.students = students;
        this.courses = courses;
        this.loading = false;
        if (!this.section) {
          this.loadError = 'This class is not available in your authorized class list.';
        }
      },
      error: () => {
        this.loading = false;
        this.loadError = 'We could not load this class. No roster or assignment data was changed.';
      },
    });
  }

  setTab(tab: ClassTab): void {
    this.activeTab = tab;
  }

  learnerName(enrollment: Enrollment): string {
    const student = this.students.find(row => row.id === enrollment.user_id);
    if (!student) {
      return 'Learner profile unavailable';
    }
    return `${student.firstname || ''} ${student.lastname || ''}`.trim() || student.username || 'Learner';
  }

  assignmentTargetLabel(assignment: Assignment): string {
    const course = this.courses.find(row => row.id === assignment.target_id);
    if (course) {
      return course.title;
    }
    return `${this.titleCase(assignment.target_type)} ${assignment.target_id}`;
  }

  requestAssignmentCreate(): void {
    this.assignmentError = '';
    if (!this.targetId.trim()) {
      this.assignmentError = 'Choose or enter the learning target before assigning.';
      return;
    }
    this.confirmationOpen = true;
  }

  cancelAssignmentCreate(): void {
    if (!this.savingAssignment) {
      this.confirmationOpen = false;
    }
  }

  createAssignment(): void {
    if (!this.sectionId || !this.targetId.trim()) {
      return;
    }
    this.savingAssignment = true;
    this.assignmentError = '';
    this.sectionsService.createAssignment(this.sectionId, {
      target_type: this.targetType,
      target_id: this.targetId.trim(),
      due_at: this.dueAt || null,
      instructions: this.instructions.trim() || null,
    }).pipe(finalize(() => {
      this.savingAssignment = false;
    })).subscribe({
      next: () => {
        this.toastService.show('Assignment created.', 'success');
        this.confirmationOpen = false;
        this.targetId = '';
        this.dueAt = '';
        this.instructions = '';
        this.loadClass();
      },
      error: (error) => {
        this.assignmentError = error?.error?.detail || 'We could not create this assignment. No learners were assigned.';
      },
    });
  }

  private titleCase(value: string): string {
    return value.replace(/[_-]/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
  }
}
