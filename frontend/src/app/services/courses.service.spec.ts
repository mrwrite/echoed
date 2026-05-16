import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { environment } from '../../environments/environment';

import { CoursesService } from './courses.service';

describe('CoursesService', () => {
  let service: CoursesService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule]
    });
    service = TestBed.inject(CoursesService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('calls the publish-readiness endpoint for a course', () => {
    service.getCoursePublishReadiness('course-1').subscribe((response) => {
      expect(response.course_id).toBe('course-1');
      expect(response.is_ready).toBeTrue();
    });

    const request = httpMock.expectOne(`${environment.apiUrl}/api/courses/course-1/publish-readiness`);
    expect(request.request.method).toBe('GET');
    request.flush({
      course_id: 'course-1',
      course_title: 'Introduction to Africa',
      is_ready: true,
      blocking_issue_count: 0,
      warning_count: 0,
      blocking_issues: [],
      warnings: [],
    });
  });

  it('calls the safe-publish endpoint for a course', () => {
    service.getCourseSafePublishValidation('course-1').subscribe((response) => {
      expect(response.course_id).toBe('course-1');
      expect(response.is_safe).toBeTrue();
    });

    const request = httpMock.expectOne(`${environment.apiUrl}/api/courses/course-1/safe-publish-validation`);
    expect(request.request.method).toBe('GET');
    request.flush({
      course_id: 'course-1',
      course_title: 'Introduction to Africa',
      is_safe: true,
      blocking_issue_count: 0,
      warning_count: 0,
      blocking_issues: [],
      warnings: [],
    });
  });

  it('calls the competency-evidence-integrity endpoint for a course', () => {
    service.getCourseCompetencyEvidenceIntegrity('course-1').subscribe((response) => {
      expect(response.course_id).toBe('course-1');
      expect(response.is_valid).toBeTrue();
      expect(response.is_explainable).toBeTrue();
    });

    const request = httpMock.expectOne(`${environment.apiUrl}/api/courses/course-1/competency-evidence-integrity`);
    expect(request.request.method).toBe('GET');
    request.flush({
      course_id: 'course-1',
      course_title: 'Introduction to Africa',
      is_valid: true,
      is_explainable: true,
      blocking_issue_count: 0,
      warning_count: 0,
      blocking_issues: [],
      warnings: [],
      affected_assessments: [],
      affected_competency_identifiers: [],
    });
  });

  it('calls the runtime-intervention endpoint for a course', () => {
    service.getCourseRuntimeInterventionRecommendations('course-1').subscribe((response) => {
      expect(response.length).toBe(1);
      expect(response[0].course_id).toBe('course-1');
      expect(response[0].recommendation_state).toBe('review');
    });

    const request = httpMock.expectOne(`${environment.apiUrl}/api/courses/course-1/runtime-intervention-recommendations`);
    expect(request.request.method).toBe('GET');
    request.flush([
      {
        student_id: 'student-1',
        student_name: 'Ada Lovelace',
        student_course_id: 'student-course-1',
        course_id: 'course-1',
        course_title: 'Introduction to Africa',
        recommendation_state: 'review',
        educator_attention_level: 'medium',
        summary: 'Recent evidence suggests a brief review conversation may help.',
        evidence_basis: [
          {
            source: 'mastery_summary',
            detail: 'Mastery evidence is mixed and explainable.',
            assessment_id: 'assessment-1',
            assessment_title: 'Practice Quiz',
            competency_identifiers: ['evidence'],
          },
        ],
        confidence_level: 'moderate',
        caution_flags: ['ambiguous_evidence'],
        learner_safe_message: 'Offer calm review support and preserve the learner\'s confidence.',
      },
    ]);
  });

  it('calls the governance-summary endpoint for a course', () => {
    service.getCourseGovernanceSummary('course-1').subscribe((response) => {
      expect(response.course_id).toBe('course-1');
      expect(response.course_title).toBe('Introduction to Africa');
      expect(response.publish_readiness.is_ready).toBeTrue();
      expect(response.safe_publish_validation.is_safe).toBeTrue();
      expect(response.lineage_safety_visibility.is_coherent).toBeTrue();
      expect(response.competency_evidence_integrity.is_valid).toBeTrue();
      expect(response.runtime_intervention_recommendations.length).toBe(1);
    });

    const request = httpMock.expectOne(`${environment.apiUrl}/api/courses/course-1/governance-summary`);
    expect(request.request.method).toBe('GET');
    request.flush({
      course_id: 'course-1',
      course_title: 'Introduction to Africa',
      publish_readiness: {
        course_id: 'course-1',
        course_title: 'Introduction to Africa',
        is_ready: true,
        blocking_issue_count: 0,
        warning_count: 0,
        blocking_issues: [],
        warnings: [],
      },
      safe_publish_validation: {
        course_id: 'course-1',
        course_title: 'Introduction to Africa',
        is_safe: true,
        blocking_issue_count: 0,
        warning_count: 0,
        blocking_issues: [],
        warnings: [],
      },
      lineage_safety_visibility: {
        course_id: 'course-1',
        course_title: 'Introduction to Africa',
        is_coherent: true,
        is_safe: true,
        blocking_issue_count: 0,
        warning_count: 0,
        blocking_issues: [],
        warnings: [],
      },
      competency_evidence_integrity: {
        course_id: 'course-1',
        course_title: 'Introduction to Africa',
        is_valid: true,
        is_explainable: true,
        blocking_issue_count: 0,
        warning_count: 0,
        blocking_issues: [],
        warnings: [],
        affected_assessments: [],
        affected_competency_identifiers: [],
      },
      runtime_intervention_recommendations: [
        {
          student_id: 'student-1',
          student_name: 'Ada Lovelace',
          student_course_id: 'student-course-1',
          course_id: 'course-1',
          course_title: 'Introduction to Africa',
          recommendation_state: 'review',
          educator_attention_level: 'medium',
          summary: 'Recent evidence suggests a brief review conversation may help.',
          evidence_basis: [
            {
              source: 'mastery_summary',
              detail: 'Mastery evidence is mixed and explainable.',
              assessment_id: 'assessment-1',
              assessment_title: 'Practice Quiz',
              competency_identifiers: ['evidence'],
            },
          ],
          confidence_level: 'moderate',
          caution_flags: ['ambiguous_evidence'],
          learner_safe_message: 'Offer calm review support and preserve the learner\'s confidence.',
        },
      ],
    });
  });
});
