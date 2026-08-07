import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { environment } from '../../environments/environment';
import { Course } from '../models/course';
import { CourseDto } from '../models/course-dto';
import { CourseDraft } from '../pages/admin/course-wizard/models/course-draft.model';
import { StartCourseRequest, SegmentResponse, CompleteSegmentResponse } from '../models/segment-response.model';
import { Lesson } from '../models/lesson';
import { StudentCourse } from '../models/student-course';
import { StudentCourseWithDetails } from '../models/student-course-with-details.model';
import {
  CourseCompetencyEvidenceIntegrity,
  CourseGovernanceSummary,
  CoursePublishReadiness,
  CourseRuntimeInterventionRecommendation,
  CourseSafePublishValidation,
} from '../models/course-publish-readiness.model';
import {
  CourseAuthoringCapabilityEnvelope,
  CourseAuthoringDraft,
  CourseLifecycleResponse,
  CourseVersionSummary,
  CourseTemplate,
} from '../models/course-authoring.model';
import { map, catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class CoursesService {
  private apiUrl = `${environment.apiUrl}/api/courses`;
  private startCourseUrl = `${environment.apiUrl}/api/start-course`;

  constructor(private http: HttpClient) { }

  getCourses(): Observable<Course[]> {
    return this.http.get<Course[]>(`${this.apiUrl}`);
  }

  getCourseById(courseId: string): Observable<CourseDraft> {
    return this.http.get<CourseDraft>(`${this.apiUrl}/${courseId}`);
  }

  getCoursePublishReadiness(courseId: string): Observable<CoursePublishReadiness> {
    return this.http.get<CoursePublishReadiness>(`${this.apiUrl}/${courseId}/publish-readiness`);
  }

  getCourseSafePublishValidation(courseId: string): Observable<CourseSafePublishValidation> {
    return this.http.get<CourseSafePublishValidation>(`${this.apiUrl}/${courseId}/safe-publish-validation`);
  }

  getCourseCompetencyEvidenceIntegrity(courseId: string): Observable<CourseCompetencyEvidenceIntegrity> {
    return this.http.get<CourseCompetencyEvidenceIntegrity>(`${this.apiUrl}/${courseId}/competency-evidence-integrity`);
  }

  getCourseRuntimeInterventionRecommendations(courseId: string): Observable<CourseRuntimeInterventionRecommendation[]> {
    return this.http.get<CourseRuntimeInterventionRecommendation[]>(`${this.apiUrl}/${courseId}/runtime-intervention-recommendations`);
  }

  getCourseGovernanceSummary(courseId: string): Observable<CourseGovernanceSummary> {
    return this.http.get<CourseGovernanceSummary>(`${this.apiUrl}/${courseId}/governance-summary`);
  }

  getLessonById(lessonId: string): Observable<Lesson> {
    return this.http.get<Lesson>(`${environment.apiUrl}/api/lessons/${lessonId}`);
  }

  uploadColoring(file: File): Observable<{ file_path: string }> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<{ file_path: string }>(
      `${environment.apiUrl}/api/upload/coloring`,
      formData
    );
  }

  uploadStorybookPage(file: File): Observable<{ file_path: string }> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<{ file_path: string }>(
      `${environment.apiUrl}/api/upload/storybook`,
      formData
    );
  }

  getCurrentSegment(studentUnitId: string): Observable<SegmentResponse> {
    return this.http.get<SegmentResponse>(
      `${environment.apiUrl}/api/progress/segment?student_unit_id=${studentUnitId}`
    );
  }


  updateCourse(courseId: string, course: CourseDraft): Observable<any> {
    return this.http.put(`${this.apiUrl}/${courseId}`, course);
  }

  deleteCourse(courseId: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${courseId}`);
  }

  enrollInCourse(courseId: string): Observable<any> {
    const payload = { course_id: courseId };
    return this.http.post(`${environment.apiUrl}/api/enroll`, payload);
  }

  assignCourseToStudent(courseId: string, studentId: string): Observable<any> {
    const payload = { course_id: courseId, student_id: studentId };
    return this.http.post(`${environment.apiUrl}/api/assign-course`, payload);
  }


  createCourse(course: CourseDraft): Observable<any> {
    return this.http.post(`${this.apiUrl}`, course);
  }

  getAuthoringCapabilities(): Observable<CourseAuthoringCapabilityEnvelope> {
    return this.http.get<CourseAuthoringCapabilityEnvelope>(
      `${environment.apiUrl}/api/course-authoring/capabilities`,
    );
  }

  getCourseAuthoringCapabilities(courseId: string): Observable<CourseAuthoringCapabilityEnvelope> {
    return this.http.get<CourseAuthoringCapabilityEnvelope>(
      `${this.apiUrl}/${courseId}/authoring-capabilities`,
    );
  }

  createAuthoringDraft(
    draft: CourseAuthoringDraft,
    idempotencyKey: string,
  ): Observable<CourseAuthoringDraft> {
    return this.http.post<CourseAuthoringDraft>(`${this.apiUrl}/authoring`, draft, {
      headers: new HttpHeaders({ 'Idempotency-Key': idempotencyKey }),
    });
  }

  getAuthoringDraft(courseId: string): Observable<CourseAuthoringDraft> {
    return this.http.get<CourseAuthoringDraft>(`${this.apiUrl}/${courseId}/authoring-draft`);
  }

  saveAuthoringDraft(courseId: string, draft: CourseAuthoringDraft): Observable<CourseAuthoringDraft> {
    return this.http.put<CourseAuthoringDraft>(`${this.apiUrl}/${courseId}/authoring-draft`, draft);
  }

  duplicateAuthoringCourse(
    courseId: string,
    title: string,
    idempotencyKey: string,
  ): Observable<CourseAuthoringDraft> {
    return this.http.post<CourseAuthoringDraft>(
      `${this.apiUrl}/${courseId}/duplicate`,
      { title },
      { headers: new HttpHeaders({ 'Idempotency-Key': idempotencyKey }) },
    );
  }

  getAuthoringPreview(courseId: string): Observable<Course> {
    return this.http.get<Course>(`${this.apiUrl}/${courseId}/authoring-preview`);
  }

  submitCourseForReview(courseId: string): Observable<CourseLifecycleResponse> {
    return this.http.post<CourseLifecycleResponse>(`${this.apiUrl}/${courseId}/submit-review`, {});
  }

  reviewCourse(
    courseId: string,
    decision: 'approved' | 'changes_requested',
    feedback: string,
  ): Observable<CourseLifecycleResponse> {
    return this.http.post<CourseLifecycleResponse>(`${this.apiUrl}/${courseId}/review`, { decision, feedback });
  }

  getCourseVersions(courseId: string): Observable<CourseVersionSummary[]> {
    return this.http.get<CourseVersionSummary[]>(`${this.apiUrl}/${courseId}/versions`);
  }

  publishCourseVersion(versionId: string): Observable<CourseVersionSummary> {
    return this.http.post<CourseVersionSummary>(`${environment.apiUrl}/api/course-versions/${versionId}/publish`, {});
  }

  getCourseTemplates(): Observable<CourseTemplate[]> {
    return this.http.get<CourseTemplate[]>(`${environment.apiUrl}/api/course-authoring/templates`);
  }

  exportCourse(courseId: string): Observable<Record<string, unknown>> {
    return this.http.get<Record<string, unknown>>(`${this.apiUrl}/${courseId}/export`);
  }

  startCourse(request: StartCourseRequest): Observable<SegmentResponse> {
    return this.http.post<SegmentResponse>(this.startCourseUrl, request);
  }

  getStudentCourses(): Observable<StudentCourseWithDetails[]> {
    return this.http.get<StudentCourseWithDetails[]>(`${environment.apiUrl}/api/student-courses`);
  }


  markSegmentCompleted(studentUnitId: string, lessonId: string): Observable<CompleteSegmentResponse> {
    const payload = {
      student_unit_id: studentUnitId,
      lesson_id: lessonId
    };

    return this.http.post<CompleteSegmentResponse>(
      `${environment.apiUrl}/api/progress/segment/complete`,
      payload
    );
  }

  /**
   * Calculate course progress as a percentage based on the current segment
   * returned from the backend. If all segments are completed a value of 100 is returned.
   */
  getCourseProgress(sc: StudentCourseWithDetails): Observable<number> {
    const unitProgressId = sc.unit_progress_id;

    if (!unitProgressId) {
      return of(0);
    }
    return this.getCurrentSegment(unitProgressId).pipe(
      map(segment => {
        if (segment.delivery_state === 'completed') {
          return 100;
        }
        if (!segment.lesson_id) {
          return 0;
        }
        const units = sc.course.units ?? [];
        const unit = units.find(u => u.lessons.some(l => l.id === segment.lesson_id));
        const lessons = unit ? unit.lessons : [];
        const total = lessons.length;
        const index = lessons.findIndex(l => l.id === segment.lesson_id);
        if (total === 0 || index === -1) {
          return 0;
        }
        return (index / total) * 100;
      }),
      catchError(err => {
        return of(0);
      })
    );
  }

}
