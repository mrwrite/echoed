import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';

import { EchoButtonComponent } from '../../components/echo-button/echo-button.component';
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
  imports: [CommonModule, FormsModule, RouterLink, EchoButtonComponent],
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

  constructor(
    private route: ActivatedRoute,
    private programsService: ProgramsService,
    private toastService: ToastService,
  ) {}

  ngOnInit(): void {
    const assessmentId = this.route.snapshot.paramMap.get('id');
    if (!assessmentId) {
      this.loading = false;
      return;
    }

    this.programsService.getAssessment(assessmentId).subscribe({
      next: (assessment) => {
        this.assessment = assessment;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
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

  submit(): void {
    if (!this.assessment || !this.canSubmit) {
      return;
    }

    this.submitting = true;
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
        this.toastService.show('Unable to submit the assessment.', 'error');
      }
    });
  }
}
