import { CommonModule } from '@angular/common';
import { Component, HostListener, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { Subject, Subscription, debounceTime, finalize, takeUntil } from 'rxjs';
import {
  AuthoringActivity,
  AuthoringLesson,
  AuthoringUnit,
  CourseAuthoringConflict,
  CourseAuthoringDraft,
  CourseAuthoringValidationIssue,
  CourseSaveState,
  CourseStudioMode,
  CourseVersionSummary,
  CourseTemplate,
  emptyCourseAuthoringDraft,
} from '../../models/course-authoring.model';
import { CourseGovernanceSummary } from '../../models/course-publish-readiness.model';
import { CoursesService } from '../../services/courses.service';
import { Course } from '../../models/course';
import { securityErrorMessage } from '../../services/security-error';
import { DiagnosticService } from '../../services/diagnostic.service';

@Component({
  selector: 'app-course-studio',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './course-studio.component.html',
  styleUrl: './course-studio.component.scss',
})
export class CourseStudioComponent implements OnInit, OnDestroy {
  readonly modes: Array<{ id: CourseStudioMode; label: string }> = [
    { id: 'setup', label: 'Setup' },
    { id: 'build', label: 'Build' },
    { id: 'quality', label: 'Quality' },
    { id: 'preview', label: 'Preview' },
    { id: 'release', label: 'Release' },
  ];
  readonly activityTypes = ['reading', 'video', 'discussion', 'quiz', 'assignment', 'storybook', 'coloring'];

  draft: CourseAuthoringDraft = emptyCourseAuthoringDraft();
  mode: CourseStudioMode = 'setup';
  saveState: CourseSaveState = 'idle';
  loading = true;
  accessDenied = false;
  notFound = false;
  loadFailure = false;
  savedAt?: Date;
  conflict?: CourseAuthoringConflict;
  localIssues: CourseAuthoringValidationIssue[] = [];
  governance?: CourseGovernanceSummary;
  learnerPreview?: Course;
  versions: CourseVersionSummary[] = [];
  templates: CourseTemplate[] = [];
  lifecycleMessage = '';
  uploadMessage = '';
  private drag?: { kind: 'unit' | 'lesson' | 'activity'; index: number };
  selectedUnit = 0;
  selectedLesson = 0;
  dirty = false;
  courseId?: string;
  private readonly changes = new Subject<void>();
  private readonly destroyed = new Subject<void>();
  private saveSubscription?: Subscription;
  private idempotencyKey = this.newKey();

  constructor(
    private readonly courses: CoursesService,
    private readonly route: ActivatedRoute,
    private readonly router: Router,
    private readonly diagnostics: DiagnosticService,
  ) {}

  ngOnInit(): void {
    this.changes.pipe(debounceTime(900), takeUntil(this.destroyed)).subscribe(() => this.save());
    this.courseId = this.route.snapshot.paramMap.get('courseId') ?? undefined;
    if (this.courseId) {
      this.loadDraft(this.courseId);
    } else {
      this.courses.getAuthoringCapabilities().subscribe({
        next: ({ capabilities }) => {
          this.loading = false;
          this.accessDenied = !capabilities.can_create;
          if (capabilities.can_create) {
            this.draft.capabilities = capabilities;
            this.courses.getCourseTemplates().subscribe({ next: templates => this.templates = templates });
          }
        },
        error: () => { this.loading = false; this.loadFailure = true; },
      });
    }
  }

  ngOnDestroy(): void {
    this.destroyed.next();
    this.destroyed.complete();
    this.saveSubscription?.unsubscribe();
  }

  @HostListener('window:beforeunload', ['$event'])
  warnBeforeUnload(event: BeforeUnloadEvent): void {
    if (this.dirty) event.preventDefault();
  }

  selectMode(mode: CourseStudioMode): void {
    this.mode = mode;
    if (mode === 'quality') this.refreshQuality();
    if (mode === 'preview' && this.courseId) this.courses.getAuthoringPreview(this.courseId).subscribe({ next: preview => this.learnerPreview = preview });
    if (mode === 'release') this.refreshVersions();
  }

  changed(): void {
    this.dirty = true;
    this.saveState = navigator.onLine ? 'dirty' : 'offline';
    this.localIssues = this.validate();
    this.changes.next();
  }

  save(): void {
    if (!this.dirty || this.saveState === 'saving' || this.accessDenied) return;
    if (!navigator.onLine) { this.saveState = 'offline'; return; }
    this.saveState = 'saving';
    const snapshot = structuredClone(this.draft);
    const snapshotJson = JSON.stringify(snapshot);
    const request = this.courseId
      ? this.courses.saveAuthoringDraft(this.courseId, snapshot)
      : this.courses.createAuthoringDraft(snapshot, this.idempotencyKey);
    this.saveSubscription = request.pipe(finalize(() => this.saveSubscription = undefined)).subscribe({
      next: saved => {
        const hadLaterChanges = JSON.stringify(this.draft) !== snapshotJson;
        if (hadLaterChanges) {
          this.draft.id = saved.id;
          this.draft.revision_number = saved.revision_number;
          this.draft.updated_at = saved.updated_at;
          this.draft.current_version_id = saved.current_version_id;
          this.draft.capabilities = saved.capabilities;
        } else {
          this.draft = saved;
        }
        this.courseId = saved.id;
        this.dirty = hadLaterChanges;
        this.saveState = hadLaterChanges ? 'dirty' : 'saved';
        this.savedAt = new Date();
        this.conflict = undefined;
        if (saved.id && this.route.snapshot.paramMap.get('courseId') !== saved.id) {
          void this.router.navigate(['/workspace/product-studio/courses', saved.id], { replaceUrl: true });
        }
        if (hadLaterChanges) this.changes.next();
      },
      error: error => {
        if (error.status === 409) {
          this.saveState = 'conflict';
          this.conflict = error.error?.detail ?? error.error;
        } else if (error.status === 422) {
          this.saveState = 'failed';
          this.localIssues = error.error?.detail?.issues ?? error.error?.issues ?? this.validate();
        } else {
          this.saveState = navigator.onLine ? 'failed' : 'offline';
          this.diagnostics.record('course_studio.autosave', error);
          this.lifecycleMessage = this.diagnostics.message('Autosave failed. Your unsaved work remains in this browser.', error);
        }
      },
    });
  }

  retry(): void { this.dirty = true; this.save(); }
  reloadServer(): void { if (this.courseId) this.loadDraft(this.courseId); }
  preserveLocalCopy(): void {
    this.courseId = undefined;
    this.draft.id = undefined;
    this.draft.revision_number = undefined;
    this.draft.title = `${this.draft.title || 'Untitled course'} (recovered copy)`;
    this.idempotencyKey = this.newKey();
    this.conflict = undefined;
    this.dirty = true;
    this.save();
  }

  addUnit(): void {
    this.draft.units.push({ title: 'Untitled unit', content: '', lessons: [] });
    this.selectedUnit = this.draft.units.length - 1; this.selectedLesson = 0; this.mode = 'build'; this.changed();
  }

  applyTemplate(templateId: string): void {
    if (!templateId) return;
    const template = this.templates.find(item => item.id === templateId);
    if (!template) return;
    const capabilities = this.draft.capabilities;
    this.draft = { ...emptyCourseAuthoringDraft(), ...structuredClone(template.course), template_id: template.id, capabilities } as CourseAuthoringDraft;
    this.changed();
  }

  exportCourse(): void {
    if (!this.courseId) return;
    this.courses.exportCourse(this.courseId).subscribe(document => {
      const url = URL.createObjectURL(new Blob([JSON.stringify(document, null, 2)], { type: 'application/json' }));
      const link = globalThis.document.createElement('a');
      link.href = url; link.download = `${this.draft.title || 'course'}.echoed.json`; link.click(); URL.revokeObjectURL(url);
    });
  }
  duplicateUnit(index: number): void { this.draft.units.splice(index + 1, 0, this.cleanUnit(this.draft.units[index])); this.changed(); }
  removeUnit(index: number): void { if (confirm(`Remove “${this.draft.units[index].title}” and its lessons?`)) { this.draft.units.splice(index, 1); this.selectedUnit = Math.max(0, Math.min(this.selectedUnit, this.draft.units.length - 1)); this.changed(); } }
  moveUnit(index: number, delta: number): void { this.move(this.draft.units, index, delta); }

  addLesson(unitIndex = this.selectedUnit): void {
    const lesson: AuthoringLesson = { title: 'Untitled lesson', key_concepts: [], discussion_questions: [], skill_tags: [], standards_metadata: {}, activities: [], sources: [] };
    this.draft.units[unitIndex].lessons.push(lesson); this.selectedUnit = unitIndex; this.selectedLesson = this.draft.units[unitIndex].lessons.length - 1; this.changed();
  }
  duplicateLesson(unitIndex: number, lessonIndex: number): void { const lessons = this.draft.units[unitIndex].lessons; lessons.splice(lessonIndex + 1, 0, this.cleanLesson(lessons[lessonIndex])); this.changed(); }
  removeLesson(unitIndex: number, lessonIndex: number): void { const lesson = this.draft.units[unitIndex].lessons[lessonIndex]; if (confirm(`Remove “${lesson.title}” and its activities?`)) { this.draft.units[unitIndex].lessons.splice(lessonIndex, 1); this.selectedLesson = Math.max(0, this.selectedLesson - 1); this.changed(); } }
  moveLesson(unitIndex: number, lessonIndex: number, delta: number): void { this.move(this.draft.units[unitIndex].lessons, lessonIndex, delta); }

  addActivity(lesson: AuthoringLesson): void { lesson.activities.push({ type: 'reading', title: 'Untitled activity', content: '', pages: [] }); this.changed(); }
  duplicateActivity(lesson: AuthoringLesson, index: number): void { const copy = structuredClone(lesson.activities[index]); this.stripIds(copy); lesson.activities.splice(index + 1, 0, copy); this.changed(); }
  removeActivity(lesson: AuthoringLesson, index: number): void { if (confirm(`Remove “${lesson.activities[index].title}”?`)) { lesson.activities.splice(index, 1); this.changed(); } }
  moveActivity(lesson: AuthoringLesson, index: number, delta: number): void { this.move(lesson.activities, index, delta); }
  addSource(lesson: AuthoringLesson): void { lesson.sources.push({ citation: '', url: null }); this.changed(); }
  uploadActivityAsset(event: Event, activity: AuthoringActivity): void {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (!file) return;
    this.uploadMessage = `Uploading ${file.name}…`;
    const upload = activity.type === 'storybook'
      ? this.courses.uploadStorybookPage(file)
      : this.courses.uploadColoring(file);
    upload.subscribe({
      next: result => {
        if (activity.type === 'storybook') activity.pages.push({ image_url: result.file_path });
        else activity.content = result.file_path;
        this.uploadMessage = `${file.name} uploaded.`;
        this.changed();
      },
      error: error => this.uploadMessage = securityErrorMessage(error, `Upload failed for ${file.name}.`),
    });
  }

  activeUnit(): AuthoringUnit | undefined { return this.draft.units[this.selectedUnit]; }
  activeLesson(): AuthoringLesson | undefined { return this.activeUnit()?.lessons[this.selectedLesson]; }
  trim(value: string): string { return value.trim(); }
  blocking(issue: CourseAuthoringValidationIssue): boolean { return issue.severity === 'blocking'; }
  setAssessmentIds(owner: { assessment_ids?: string[] }, value: string): void { owner.assessment_ids = value.split(',').map(item => item.trim()).filter(Boolean); this.changed(); }
  startDrag(kind: 'unit' | 'lesson' | 'activity', index: number, event: DragEvent): void { event.stopPropagation(); this.drag = { kind, index }; event.dataTransfer?.setData('text/plain', `${kind}:${index}`); }
  dropUnit(index: number, event: DragEvent): void { event.preventDefault(); if (this.drag?.kind === 'unit') this.reorder(this.draft.units, this.drag.index, index); }
  dropLesson(unit: AuthoringUnit, index: number, event: DragEvent): void { event.preventDefault(); if (this.drag?.kind === 'lesson') this.reorder(unit.lessons, this.drag.index, index); }
  dropActivity(lesson: AuthoringLesson, index: number, event: DragEvent): void { event.preventDefault(); if (this.drag?.kind === 'activity') this.reorder(lesson.activities, this.drag.index, index); }

  focusIssue(issue: CourseAuthoringValidationIssue): void {
    this.mode = issue.entity_type === 'course' ? 'setup' : 'build';
    setTimeout(() => {
      const exact = document.getElementById(issue.entity_id ? `entity-${issue.entity_id}` : `field-${issue.field}`);
      (exact ?? document.querySelector<HTMLElement>(`[data-authoring-field="${issue.field}"]`))?.focus();
    });
  }

  refreshQuality(): void {
    this.localIssues = this.validate();
    if (this.courseId) this.courses.getCourseGovernanceSummary(this.courseId).subscribe({ next: value => this.governance = value });
  }

  submitForReview(): void {
    if (!this.courseId || this.dirty) return;
    this.courses.submitCourseForReview(this.courseId).subscribe({
      next: result => { this.draft.revision_status = result.lifecycle_state; this.lifecycleMessage = 'Submitted for independent review.'; },
      error: error => { this.lifecycleMessage = error.error?.detail?.code === 'course_not_ready_for_review' ? 'Complete the required course structure before review.' : 'Submission failed. Your draft was not changed.'; },
    });
  }

  recordReview(): void {
    if (!this.courseId) return;
    const feedback = prompt('Enter review feedback for the creator:');
    if (!feedback?.trim()) return;
    const approved = confirm('Approve this course? Select Cancel to return it for changes.');
    this.courses.reviewCourse(this.courseId, approved ? 'approved' : 'changes_requested', feedback.trim()).subscribe({
      next: result => { this.draft.revision_status = result.lifecycle_state; this.lifecycleMessage = approved ? 'Course approved.' : 'Course returned for changes.'; },
      error: () => this.lifecycleMessage = 'Review decision could not be saved.',
    });
  }

  publish(): void {
    const draftVersion = this.versions.find(version => version.status === 'draft');
    if (!draftVersion) { this.lifecycleMessage = 'No draft version is available to publish.'; return; }
    this.courses.publishCourseVersion(draftVersion.id).subscribe({
      next: () => { this.draft.revision_status = 'published'; this.lifecycleMessage = 'The approved version is published.'; this.refreshVersions(); },
      error: error => {
        if (error.status === 422) {
          this.lifecycleMessage = 'Safe-publish checks found blocking issues.';
        } else {
          this.diagnostics.record('course_studio.publish', error);
          this.lifecycleMessage = this.diagnostics.message('Publication failed without changing learner availability.', error);
        }
      },
    });
  }

  private refreshVersions(): void {
    if (this.courseId) this.courses.getCourseVersions(this.courseId).subscribe({ next: versions => this.versions = versions });
  }

  private loadDraft(courseId: string): void {
    this.loading = true; this.notFound = false; this.loadFailure = false; this.accessDenied = false;
    this.courses.getAuthoringDraft(courseId).subscribe({
      next: draft => { this.draft = draft; this.loading = false; this.dirty = false; this.saveState = 'idle'; this.localIssues = this.validate(); },
      error: error => { this.loading = false; this.accessDenied = error.status === 403; this.notFound = error.status === 404; this.loadFailure = !this.accessDenied && !this.notFound; },
    });
  }

  private validate(): CourseAuthoringValidationIssue[] {
    const issues: CourseAuthoringValidationIssue[] = [];
    const add = (severity: 'blocking' | 'warning' | 'recommendation', entity_type: string, field: string, message: string, corrective_context: string, entity_id?: string) => issues.push({ severity, entity_type, entity_id, field, message, corrective_context });
    if (!this.draft.title.trim()) add('blocking', 'course', 'title', 'Add a course title.', 'Use a clear learner-facing title.');
    if (!this.draft.description.trim()) add('warning', 'course', 'description', 'Add a course description.', 'Explain what learners will know or do.');
    if (!this.draft.learning_objectives?.trim()) add('warning', 'course', 'learning_objectives', 'Add measurable learning objectives.', 'Start objectives with observable actions.');
    if (!this.draft.units.length) add('blocking', 'course', 'units', 'Add at least one unit.', 'Use Build to create the course outline.');
    this.draft.units.forEach((unit, ui) => {
      if (!unit.title.trim()) add('blocking', 'unit', 'title', `Unit ${ui + 1} needs a title.`, 'Name the unit for its central concept.', unit.id);
      if (!unit.lessons.length) add('blocking', 'unit', 'lessons', `“${unit.title}” needs a lesson.`, 'Add at least one lesson.', unit.id);
      unit.lessons.forEach((lesson, li) => {
        if (!lesson.title.trim()) add('blocking', 'lesson', 'title', `Lesson ${li + 1} needs a title.`, 'Name the lesson for its learning goal.', lesson.id);
        if (!lesson.objective?.trim() && !lesson.learning_objectives?.trim()) add('warning', 'lesson', 'objective', `“${lesson.title}” needs an objective.`, 'Describe an observable learner outcome.', lesson.id);
        lesson.activities.forEach(activity => {
          if (!activity.title.trim()) add('blocking', 'activity', 'title', 'An activity needs a title.', 'Add a brief learner-facing title.', activity.id);
          if (!activity.content.trim()) add('warning', 'activity', 'content', `“${activity.title}” has no instructions.`, 'Add accessible text instructions or a transcript.', activity.id);
          if (activity.type === 'storybook' && !activity.pages.length) add('warning', 'activity', 'pages', `“${activity.title}” has no storybook pages.`, 'Upload at least one page and provide accessible instructions.', activity.id);
        });
        if (!lesson.assessment?.trim() && !lesson.assessment_ids?.length) add('warning', 'lesson', 'assessment_ids', `“${lesson.title}” has no assessment evidence.`, 'Add a check for understanding or reference an assessment.', lesson.id);
        lesson.sources.forEach(source => {
          if (!source.citation.trim()) add('blocking', 'source', 'citation', 'A source is missing its citation.', 'Add enough attribution for a reviewer to identify the source.', source.id);
        });
      });
    });
    return issues;
  }

  private move<T>(items: T[], index: number, delta: number): void { this.reorder(items, index, index + delta); }
  private reorder<T>(items: T[], from: number, to: number): void { if (to < 0 || to >= items.length || from === to) return; const [item] = items.splice(from, 1); items.splice(to, 0, item); this.drag = undefined; this.changed(); }
  private cleanUnit(unit: AuthoringUnit): AuthoringUnit { const copy = structuredClone(unit); this.stripIds(copy); copy.title += ' (copy)'; return copy; }
  private cleanLesson(lesson: AuthoringLesson): AuthoringLesson { const copy = structuredClone(lesson); this.stripIds(copy); copy.title += ' (copy)'; return copy; }
  private stripIds(value: unknown): void { if (!value || typeof value !== 'object') return; if ('id' in value) delete (value as { id?: string }).id; Object.values(value).forEach(child => Array.isArray(child) ? child.forEach(item => this.stripIds(item)) : this.stripIds(child)); }
  private newKey(): string { return globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`; }
}
