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
});
