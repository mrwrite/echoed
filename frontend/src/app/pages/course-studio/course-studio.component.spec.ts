import { HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { fakeAsync, TestBed, tick } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { of, Subject, throwError } from 'rxjs';
import { CourseAuthoringCapabilities, CourseAuthoringDraft, emptyCourseAuthoringDraft } from '../../models/course-authoring.model';
import { CoursesService } from '../../services/courses.service';
import { CourseStudioComponent } from './course-studio.component';

describe('CourseStudioComponent', () => {
  let courses: jasmine.SpyObj<CoursesService>;
  const capabilities: CourseAuthoringCapabilities = {
    can_create: true, can_view_draft: true, can_edit: true, can_duplicate: true,
    can_preview: true, can_submit_review: true, can_review: false, can_publish: false,
  };

  beforeEach(async () => {
    courses = jasmine.createSpyObj<CoursesService>('CoursesService', [
      'getAuthoringCapabilities', 'getCourseTemplates', 'createAuthoringDraft',
      'saveAuthoringDraft', 'getAuthoringDraft', 'getCourseGovernanceSummary',
      'getAuthoringPreview', 'getCourseVersions', 'submitCourseForReview',
      'reviewCourse', 'publishCourseVersion', 'exportCourse',
    ]);
    courses.getAuthoringCapabilities.and.returnValue(of({ capabilities }));
    courses.getCourseTemplates.and.returnValue(of([]));
    await TestBed.configureTestingModule({
      imports: [CourseStudioComponent, RouterTestingModule],
      providers: [
        { provide: CoursesService, useValue: courses },
        { provide: ActivatedRoute, useValue: { snapshot: { paramMap: { get: () => null } } } },
      ],
    }).compileComponents();
  });

  it('opens a blank studio only when the backend allows creation', () => {
    const fixture = TestBed.createComponent(CourseStudioComponent);
    fixture.detectChanges();
    expect(fixture.componentInstance.accessDenied).toBeFalse();
    expect(fixture.componentInstance.draft.capabilities?.can_create).toBeTrue();
    expect(fixture.nativeElement.querySelector('h2').textContent).toContain('Outline');
  });

  it('uses one debounced idempotent create and keeps deterministic outline order', fakeAsync(() => {
    spyOn(TestBed.inject(Router), 'navigate').and.resolveTo(true);
    const fixture = TestBed.createComponent(CourseStudioComponent);
    fixture.detectChanges();
    const component = fixture.componentInstance;
    const saved: CourseAuthoringDraft = { ...emptyCourseAuthoringDraft(), id: 'course-1', title: 'History', description: 'Desc', revision_number: 1, revision_status: 'draft', updated_at: new Date().toISOString(), units: [], capabilities };
    courses.createAuthoringDraft.and.returnValue(of(saved));
    component.draft.title = 'History'; component.draft.description = 'Desc';
    component.addUnit(); component.addUnit(); component.moveUnit(1, -1);
    tick(899);
    expect(courses.createAuthoringDraft).not.toHaveBeenCalled();
    tick(1);
    expect(courses.createAuthoringDraft).toHaveBeenCalledTimes(1);
    expect(courses.createAuthoringDraft.calls.mostRecent().args[1]).toBeTruthy();
  }));

  it('retains local content and offers bounded recovery after a revision conflict', () => {
    const fixture = TestBed.createComponent(CourseStudioComponent);
    fixture.detectChanges();
    const component = fixture.componentInstance;
    component.draft.title = 'Local work';
    component.saveState = 'conflict';
    component.conflict = { code: 'course_authoring_revision_conflict', course_id: 'course-1', current_revision: 3 };
    fixture.detectChanges();
    expect(component.draft.title).toBe('Local work');
    expect(fixture.nativeElement.textContent).toContain('changed elsewhere');
  });

  it('serializes autosaves and queues edits made during an in-flight write', fakeAsync(() => {
    spyOn(TestBed.inject(Router), 'navigate').and.resolveTo(true);
    const fixture = TestBed.createComponent(CourseStudioComponent);
    fixture.detectChanges();
    const component = fixture.componentInstance;
    const firstWrite = new Subject<CourseAuthoringDraft>();
    courses.createAuthoringDraft.and.returnValue(firstWrite);
    courses.saveAuthoringDraft.and.returnValue(of({ ...emptyCourseAuthoringDraft(), id: 'course-1', title: 'Second edit', description: '', revision_number: 2, revision_status: 'draft', units: [], capabilities }));
    component.draft.title = 'First edit'; component.changed(); tick(900);
    expect(courses.createAuthoringDraft).toHaveBeenCalledTimes(1);
    component.draft.title = 'Second edit'; component.changed(); tick(900);
    expect(courses.saveAuthoringDraft).not.toHaveBeenCalled();
    firstWrite.next({ ...emptyCourseAuthoringDraft(), id: 'course-1', title: 'First edit', description: '', revision_number: 1, revision_status: 'draft', units: [], capabilities });
    firstWrite.complete(); tick(900);
    expect(courses.saveAuthoringDraft).toHaveBeenCalledTimes(1);
    expect(courses.saveAuthoringDraft.calls.mostRecent().args[1].title).toBe('Second edit');
  }));

  it('retries a failed create with the same idempotency key', fakeAsync(() => {
    const fixture = TestBed.createComponent(CourseStudioComponent);
    fixture.detectChanges();
    const component = fixture.componentInstance;
    courses.createAuthoringDraft.and.returnValue(throwError(() => ({ status: 503 })));
    component.draft.title = 'Recoverable'; component.changed(); tick(900);
    const firstKey = courses.createAuthoringDraft.calls.mostRecent().args[1];
    expect(component.saveState).toBe('failed');
    courses.createAuthoringDraft.and.returnValue(of({ ...emptyCourseAuthoringDraft(), id: 'course-1', title: 'Recoverable', description: '', revision_number: 1, revision_status: 'draft', units: [], capabilities }));
    spyOn(TestBed.inject(Router), 'navigate').and.resolveTo(true);
    component.retry();
    expect(courses.createAuthoringDraft.calls.mostRecent().args[1]).toBe(firstKey);
  }));

  it('preserves local work and exposes a safe autosave support reference', fakeAsync(() => {
    spyOn(console, 'warn');
    const fixture = TestBed.createComponent(CourseStudioComponent);
    fixture.detectChanges();
    const component = fixture.componentInstance;
    const failure = new HttpErrorResponse({
      status: 500,
      headers: new HttpHeaders({ 'X-Request-ID': 'req-autosave' }),
      error: { detail: 'internal database details' },
    });
    courses.createAuthoringDraft.and.returnValue(throwError(() => failure));
    component.draft.title = 'Work that must survive';
    component.changed();
    tick(900);
    expect(component.draft.title).toBe('Work that must survive');
    expect(component.dirty).toBeTrue();
    expect(component.lifecycleMessage).toContain('Reference: req-autosave');
    expect(component.lifecycleMessage).not.toContain('database');
  }));

  it('reports publish failure safely without changing the draft lifecycle', () => {
    spyOn(console, 'warn');
    const fixture = TestBed.createComponent(CourseStudioComponent);
    fixture.detectChanges();
    const component = fixture.componentInstance;
    component.draft.revision_status = 'approved';
    component.versions = [{ id: 'version-1', course_id: 'course-1', version_number: 1, status: 'draft', created_at: '' }];
    courses.publishCourseVersion.and.returnValue(throwError(() => new HttpErrorResponse({
      status: 500,
      headers: new HttpHeaders({ 'X-Request-ID': 'req-publish' }),
    })));
    component.publish();
    expect(component.draft.revision_status).toBe('approved');
    expect(component.lifecycleMessage).toContain('Reference: req-publish');
  });
});
