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
});
