import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of, Subject, throwError } from 'rxjs';

import { AssessmentDetailComponent } from './assessment-detail.component';
import { ProgramsService } from '../../services/programs.service';
import { ToastService } from '../../services/toast.service';

function buildAvailableAssessment() {
  return {
    id: 'assessment-available',
    title: 'Available Assessment',
    description: 'Ready for learners',
    lesson_id: null,
    course_id: null,
    program_id: null,
    assessment_scope: 'lesson',
    assessment_state: 'published',
    availability_state: 'available',
    learner_delivery_state: 'available',
    learner_delivery_detail: '',
    is_available_for_learner: true,
    passing_score: 80,
    max_attempts: null,
    policy_metadata: {},
    lifecycle_metadata: {},
    created_by: null,
    created_at: new Date().toISOString(),
    questions: [
      {
        id: 'question-1',
        prompt: 'What is 2 + 2?',
        question_type: 'multiple_choice',
        order: 1,
        choices: ['4', '5'],
        points: 5,
      },
    ],
  };
}

describe('AssessmentDetailComponent', () => {
  let component: AssessmentDetailComponent;
  let fixture: ComponentFixture<AssessmentDetailComponent>;
  let programsServiceSpy: jasmine.SpyObj<ProgramsService>;
  let toastServiceSpy: jasmine.SpyObj<ToastService>;

  beforeEach(async () => {
    programsServiceSpy = jasmine.createSpyObj<ProgramsService>('ProgramsService', [
      'getAssessment',
      'submitAssessment',
      'getCertifications',
      'evaluateCertification',
    ]);
    toastServiceSpy = jasmine.createSpyObj<ToastService>('ToastService', ['show']);

    programsServiceSpy.getAssessment.and.returnValue(
      of({
        id: 'assessment-1',
        title: 'Locked Assessment',
        description: 'Not for learners yet',
        lesson_id: null,
        course_id: null,
        program_id: null,
        assessment_scope: 'lesson',
        assessment_state: 'draft',
        availability_state: 'unavailable',
        learner_delivery_state: 'draft',
        learner_delivery_detail: 'This assessment is not yet published.',
        is_available_for_learner: false,
        passing_score: 80,
        max_attempts: null,
        policy_metadata: {},
        lifecycle_metadata: {},
        created_by: null,
        created_at: new Date().toISOString(),
        questions: [],
      })
    );

    await TestBed.configureTestingModule({
      imports: [CommonModule, RouterTestingModule, AssessmentDetailComponent],
      providers: [
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              paramMap: {
                get: () => 'assessment-1',
              },
            },
          },
        },
        { provide: ProgramsService, useValue: programsServiceSpy },
        { provide: ToastService, useValue: toastServiceSpy },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AssessmentDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('hides the submission form and blocks submit for unavailable assessments', () => {
    expect(component.isAvailableForLearner).toBeFalse();
    expect(component.canSubmit).toBeFalse();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Assessment not ready for learner submission');
    expect(compiled.textContent).not.toContain('Submit Assessment');
    expect(compiled.querySelector('[data-echo-state="unavailable"]')).not.toBeNull();
  });

  it('renders a retry-capable error state when the assessment cannot be loaded', () => {
    programsServiceSpy.getAssessment.and.returnValue(
      throwError(() => new Error('load failed')),
    );

    fixture = TestBed.createComponent(AssessmentDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('[data-echo-state="error"]')).not.toBeNull();
    expect(compiled.textContent).toContain('We could not load this assessment');
    expect(compiled.textContent).toContain('Retry');
  });

  it('renders the canonical loading state while the assessment is resolving', () => {
    const pendingAssessment = new Subject<any>();
    programsServiceSpy.getAssessment.and.returnValue(pendingAssessment.asObservable());

    fixture = TestBed.createComponent(AssessmentDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('[data-echo-loading="page"]')).not.toBeNull();
    expect(compiled.textContent).toContain('Preparing assessment');
  });

  it('shows a clear submit-pending state without changing submit behavior', () => {
    const pendingSubmit = new Subject<any>();
    programsServiceSpy.getAssessment.and.returnValue(of(buildAvailableAssessment()));
    programsServiceSpy.submitAssessment.and.returnValue(pendingSubmit.asObservable());

    fixture = TestBed.createComponent(AssessmentDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    component.answers['question-1'] = '4';
    fixture.detectChanges();

    component.submit();
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(component.submitting).toBeTrue();
    expect(compiled.querySelector('form')?.getAttribute('aria-busy')).toBe('true');
    expect(compiled.querySelector('[data-echo-loading="compact"]')).not.toBeNull();
    expect(compiled.textContent).toContain('Submitting assessment');
  });

  it('renders an accessible failure state after submit errors', () => {
    programsServiceSpy.getAssessment.and.returnValue(of(buildAvailableAssessment()));
    programsServiceSpy.submitAssessment.and.returnValue(throwError(() => new Error('submit failed')));

    fixture = TestBed.createComponent(AssessmentDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();

    component.answers['question-1'] = '4';
    fixture.detectChanges();
    component.submit();
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const failurePanel = compiled.querySelector('[data-echo-state="error"]');
    expect(failurePanel).not.toBeNull();
    expect(failurePanel?.getAttribute('role')).toBe('alert');
    expect(failurePanel?.getAttribute('aria-label')).toBe('We could not submit your assessment');
    expect(compiled.textContent).toContain('We could not submit your assessment');
  });
});
