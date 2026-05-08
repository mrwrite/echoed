import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { AssessmentDetailComponent } from './assessment-detail.component';
import { ProgramsService } from '../../services/programs.service';
import { ToastService } from '../../services/toast.service';

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
    expect(compiled.textContent).toContain('Assessment unavailable for learners');
    expect(compiled.textContent).not.toContain('Submit Assessment');
  });
});
