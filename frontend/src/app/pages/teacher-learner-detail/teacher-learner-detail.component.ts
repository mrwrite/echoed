import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';

import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { Enrollment, Section } from '../../models/section';
import { User } from '../../models/user';
import { SectionsService } from '../../services/sections.service';
import { UsersService } from '../../services/users.service';

@Component({
  selector: 'app-teacher-learner-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, EchoLoadingStateComponent, EchoStatePanelComponent],
  template: `
    <section class="teacher-learner" aria-labelledby="teacher-learner-title">
      <a [routerLink]="sectionId ? ['/teach/classes', sectionId] : ['/teach/classes']" class="teacher-learner__back">Back to class</a>

      <app-echo-loading-state
        *ngIf="loading"
        density="page"
        ariaLabel="teacher-learner-loading"
        title="Loading learner"
        body="We are checking class context before showing learner details."
      ></app-echo-loading-state>
      <app-echo-state-panel
        *ngIf="!loading && loadError"
        variant="permission"
        eyebrow="Learner unavailable"
        title="We could not show this learner"
        [body]="loadError"
      ></app-echo-state-panel>

      <ng-container *ngIf="!loading && !loadError && learner">
        <header class="teacher-learner__header">
          <div>
            <p class="teacher-learner__eyebrow">Learner detail</p>
            <h1 id="teacher-learner-title">{{ learnerName }}</h1>
            <p>{{ section?.name || 'Class context verified from roster' }}</p>
          </div>
        </header>

        <section class="teacher-learner__panel" aria-labelledby="learner-current-heading">
          <p class="teacher-learner__eyebrow">Current learning</p>
          <h2 id="learner-current-heading">Class-scoped information</h2>
          <dl>
            <div>
              <dt>Enrollment status</dt>
              <dd>{{ enrollment?.status | titlecase }}</dd>
            </div>
            <div>
              <dt>Role in class</dt>
              <dd>{{ enrollment?.role_in_section | titlecase }}</dd>
            </div>
            <div>
              <dt>Joined</dt>
              <dd>{{ enrollment?.enrolled_at ? (enrollment?.enrolled_at | date:'MMM d, y') : 'Unavailable' }}</dd>
            </div>
          </dl>
        </section>

        <section class="teacher-learner__panel" aria-labelledby="learner-progress-heading">
          <p class="teacher-learner__eyebrow">Progress and assessment</p>
          <h2 id="learner-progress-heading">Supported states</h2>
          <div class="teacher-learner__states">
            <article>
              <strong>Assignment status</strong>
              <p>Unavailable in this detail view. The current assignment API does not expose per-learner assignment state to teachers.</p>
            </article>
            <article>
              <strong>Course progress</strong>
              <p>Use the Teach overview for existing teacher summary rows. A class-scoped learner progress endpoint is not verified.</p>
            </article>
            <article>
              <strong>Assessment results</strong>
              <p>Auto-scored assessment reporting endpoints exist, but this page does not infer assessment scope without a course, unit, lesson, or program target.</p>
            </article>
            <article>
              <strong>Feedback history</strong>
              <p>Feedback unavailable. No teacher feedback persistence endpoint is verified.</p>
            </article>
          </div>
        </section>
      </ng-container>
    </section>
  `,
  styleUrl: './teacher-learner-detail.component.scss',
})
export class TeacherLearnerDetailComponent implements OnInit {
  learnerId = '';
  sectionId = '';
  learner?: User;
  section?: Section;
  enrollment?: Enrollment;
  loading = true;
  loadError = '';

  constructor(
    private route: ActivatedRoute,
    private sectionsService: SectionsService,
    private usersService: UsersService,
  ) {}

  ngOnInit(): void {
    this.learnerId = this.route.snapshot.paramMap.get('learnerId') || '';
    this.sectionId = this.route.snapshot.queryParamMap.get('sectionId') || '';
    this.loadLearner();
  }

  get learnerName(): string {
    if (!this.learner) {
      return 'Learner';
    }
    return `${this.learner.firstname || ''} ${this.learner.lastname || ''}`.trim() || this.learner.username || 'Learner';
  }

  loadLearner(): void {
    if (!this.learnerId || !this.sectionId) {
      this.loading = false;
      this.loadError = 'Open a learner from a class roster so class authorization can be verified.';
      return;
    }

    this.loading = true;
    this.loadError = '';
    forkJoin({
      sections: this.sectionsService.listSections(),
      roster: this.sectionsService.getRoster(this.sectionId),
      students: this.usersService.getStudents().pipe(catchError(() => of([] as User[]))),
    }).subscribe({
      next: ({ sections, roster, students }) => {
        this.section = sections.find(section => section.id === this.sectionId);
        this.enrollment = roster.find(row => row.user_id === this.learnerId);
        this.learner = students.find(student => student.id === this.learnerId);
        this.loading = false;
        if (!this.section || !this.enrollment) {
          this.loadError = 'This learner is not available in the selected authorized class roster.';
          return;
        }
        if (!this.learner) {
          this.loadError = 'The learner enrollment exists, but the authorized student profile list did not include profile details.';
        }
      },
      error: () => {
        this.loading = false;
        this.loadError = 'We could not verify this learner against the class roster.';
      },
    });
  }
}
