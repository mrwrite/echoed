import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { environment } from '../../environments/environment';
import { AnalyticsService } from './analytics.service';

describe('AnalyticsService', () => {
  let service: AnalyticsService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule]
    });

    service = TestBed.inject(AnalyticsService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('does not manually attach an Authorization header to admin overview requests', () => {
    service.getAdminOverview().subscribe();

    const req = httpMock.expectOne(`${environment.apiUrl}/api/analytics/overview`);
    expect(req.request.headers.has('Authorization')).toBeFalse();
    req.flush({
      totals: {
        students: 0,
        teachers: 0,
        courses: 0,
        active_students: 0,
        total_enrollments: 0,
        pending_enrollments: 0
      },
      progress: {
        lessons_completed: 0,
        units_completed: 0,
        courses_completed: 0,
        course_completion_rate: 0
      }
    });
  });

  it('loads read-only Analytics V2 endpoints', () => {
    service.getV2WorkspaceAnalytics().subscribe(response => {
      expect(response.totals.total_products).toBe(2);
    });
    const workspaceReq = httpMock.expectOne(`${environment.apiUrl}/api/analytics/workspace`);
    expect(workspaceReq.request.method).toBe('GET');
    workspaceReq.flush({
      totals: {
        total_products: 2,
        total_projects: 1,
        total_knowledge_sources: 1,
        total_artifacts: 1,
        total_generation_runs: 1,
        total_access_grants: 1,
        learner_count: 1,
        enrollment_count: 1,
        course_backed_product_count: 1,
        program_backed_product_count: 0
      },
      products_by_type: { course: 1, resource_pack: 1 },
      products_by_status: { published: 1, draft: 1 },
      artifacts_by_status: { in_review: 1 },
      artifacts_by_type: { guide: 1 },
      generation_runs_by_status: { completed: 1 },
      access_grants_by_status: { active: 1 },
      access_grants_by_type: { manual: 1 },
      review_health: { draft_products: 1 },
      learner_engagement: { learner_count: 1 },
      recent: { products: [], artifacts: [], knowledge_sources: [] },
      event_tracking: { status: 'unavailable', message: 'No events yet.' },
      scoped_product_count: 2
    });

    service.getV2ProductAnalytics().subscribe(response => {
      expect(response.total_products).toBe(2);
    });
    const productReq = httpMock.expectOne(`${environment.apiUrl}/api/analytics/products`);
    expect(productReq.request.method).toBe('GET');
    productReq.flush({
      total_products: 2,
      course_backed_product_count: 1,
      program_backed_product_count: 0,
      products_by_type: { course: 1, resource_pack: 1 },
      products_by_status: { published: 1, draft: 1 },
      products: []
    });

    service.getV2LearnerAnalytics().subscribe(response => {
      expect(response.summary['learner_count']).toBe(1);
    });
    const learnerReq = httpMock.expectOne(`${environment.apiUrl}/api/analytics/learners`);
    expect(learnerReq.request.method).toBe('GET');
    learnerReq.flush({
      summary: { learner_count: 1 },
      enrollments_by_status: { active: 1 },
      access_grants_by_status: { active: 1 },
      access_grants_by_type: { manual: 1 }
    });

    service.getV2KnowledgePipelineAnalytics().subscribe(response => {
      expect(response.total_artifacts).toBe(1);
    });
    const pipelineReq = httpMock.expectOne(`${environment.apiUrl}/api/analytics/knowledge-pipeline`);
    expect(pipelineReq.request.method).toBe('GET');
    pipelineReq.flush({
      total_projects: 1,
      total_knowledge_sources: 1,
      total_artifacts: 1,
      total_generation_runs: 1,
      knowledge_sources_by_type: { lesson_source: 1 },
      knowledge_sources_by_status: { available: 1 },
      artifacts_by_status: { in_review: 1 },
      artifacts_by_type: { guide: 1 },
      generation_runs_by_status: { completed: 1 },
      recent: { artifacts: [], knowledge_sources: [] },
      source_coverage: { status: 'advisory', artifacts_with_knowledge_source: 1 }
    });
  });
});
