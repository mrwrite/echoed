import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { environment } from '../../environments/environment';
import { Course } from '../models/course';
import { CourseDto } from '../models/course-dto';
import { CourseDraft } from '../pages/admin/course-wizard/models/course-draft.model';
import { StartCourseRequest, SegmentResponse, CompleteSegmentResponse } from '../models/segment-response.model';
import { Lesson } from '../models/lesson';
import { StudentCourse } from '../models/student-course';
import { StudentCourseWithDetails } from '../models/student-course-with-details.model';
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
