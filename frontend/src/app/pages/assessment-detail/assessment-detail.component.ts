import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';

import { EchoButtonComponent } from '../../components/echo-button/echo-button.component';
import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import {
  Assessment,
  AssessmentAttemptResult,
  CertificationEvaluationResult,
} from '../../models/program';
import { ProgramsService } from '../../services/programs.service';
import { ToastService } from '../../services/toast.service';

@Component({
  selector: 'app-assessment-detail',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, EchoButtonComponent, EchoLoadingStateComponent, EchoStatePanelComponent],
  templateUrl: './assessment-detail.component.html',
  styleUrl: './assessment-detail.component.scss'
})
export class AssessmentDetailComponent implements OnInit {
  assessment?: Assessment;
  answers: Record<string, string> = {};
  result?: AssessmentAttemptResult;
  awardedCertifications: CertificationEvaluationResult[] = [];
  loading = true;
  submitting = false;
  loadErrorMessage = '';
  submitErrorMessage = '';

  constructor(
    private route: ActivatedRoute,
    private programsService: ProgramsService,
    private toastService: ToastService,
  ) {}

  ngOnInit(): void {
    this.loadAssessment();
  }

  loadAssessment(): void {
    const assessmentId = this.route.snapshot.paramMap.get('id');
    if (!assessmentId) {
      this.loading = false;
      this.loadErrorMessage = 'We could not determine which assessment to load.';
      return;
    }

    this.loading = true;
    this.loadErrorMessage = '';
    this.programsService.getAssessment(assessmentId).subscribe({
      next: (assessment) => {
        this.assessment = assessment;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.assessment = undefined;
        this.loadErrorMessage = 'Unable to load the assessment right now. Retry to restore the latest assessment state.';
        this.toastService.show('Unable to load the assessment.', 'error');
      }
    });
  }

  get canSubmit(): boolean {
    return !!this.assessment
      && this.isAvailableForLearner
      && this.assessment.questions.every(question => !!this.answers[question.id]?.trim())
      && !this.submitting;
  }

  get isAvailableForLearner(): boolean {
    return this.assessment?.is_available_for_learner !== false;
  }

  get deliveryStateLabel(): string {
    return this.assessment?.learner_delivery_state || 'available';
  }

  get deliveryStateDetail(): string {
    return this.assessment?.learner_delivery_detail || 'This assessment is not available right now.';
  }

  get submissionStatusMessage(): string {
    return this.assessment?.program_id
      ? 'Submitting your assessment and refreshing any related certification results.'
      : 'Submitting your assessment and saving your latest learner evidence.';
  }

  submit(): void {
    if (!this.assessment || !this.canSubmit) {
      return;
    }

    this.submitting = true;
    this.submitErrorMessage = '';
    this.awardedCertifications = [];
    const payload = this.assessment.questions.map(question => ({
      question_id: question.id,
      answer: this.answers[question.id],
    }));

    this.programsService.submitAssessment(this.assessment.id, payload).subscribe({
      next: (result) => {
        this.result = result;
        if (!this.assessment?.program_id) {
          this.submitting = false;
          this.toastService.show('Assessment submitted.', result.passed ? 'success' : 'error');
          return;
        }

        this.programsService.getCertifications(this.assessment.program_id).subscribe({
          next: (certifications) => {
            if (certifications.length === 0) {
              this.submitting = false;
              this.toastService.show('Assessment submitted.', result.passed ? 'success' : 'error');
              return;
            }

            forkJoin(certifications.map(certification => this.programsService.evaluateCertification(certification.id))).subscribe({
              next: (evaluations) => {
                this.awardedCertifications = evaluations.filter(evaluation => evaluation.awarded);
                this.submitting = false;
                this.toastService.show(
                  this.awardedCertifications.length > 0
                    ? 'Assessment submitted and certification status updated.'
                    : 'Assessment submitted.',
                  result.passed ? 'success' : 'error'
                );
              },
              error: () => {
                this.submitting = false;
                this.toastService.show('Assessment submitted, but certification status could not be refreshed.', 'error');
              }
            });
          },
          error: () => {
            this.submitting = false;
            this.toastService.show('Assessment submitted.', result.passed ? 'success' : 'error');
          }
        });
      },
      error: () => {
        this.submitting = false;
        this.submitErrorMessage = 'We could not submit this assessment. Your answers are still here, so review them and try again.';
        this.toastService.show('Unable to submit the assessment.', 'error');
      }
    });
  }

  retryLoad(): void {
    this.loadAssessment();
  }
}
