import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { AuthService } from './auth.service';
import { environment } from '../../environments/environment';
import { Course } from '../models/course';
import { CourseDto } from '../models/course-dto';
import { CourseDraft } from '../pages/admin/course-wizard/models/course-draft.model';
import { StartCourseRequest, SegmentResponse } from '../models/segment-response.model';
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

  constructor(private http: HttpClient, private authService: AuthService) { }

  private getHeaders(): HttpHeaders {
    let token = this.authService.getToken();
    if (token && !token.startsWith('Bearer ')) {
      token = `Bearer ${token}`;
    } else if (!token) {
      token = `Bearer ${this.authService.getToken()}`;
    }
    return new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: token || ''
    });
  }

  getCourses(): Observable<Course[]> {
    return this.http.get<Course[]>(`${this.apiUrl}`, { headers: this.getHeaders() });
  }

  getCourseById(courseId: string): Observable<CourseDraft> {
    return this.http.get<CourseDraft>(`${this.apiUrl}/${courseId}`, { headers: this.getHeaders() });
  }

  getLessonById(lessonId: string): Observable<Lesson> {
  return this.http.get<Lesson>(`${environment.apiUrl}/api/lessons/${lessonId}`, {
    headers: this.getHeaders()
  });
}

  uploadColoring(file: File): Observable<{ file_path: string }> {
    const formData = new FormData();
    formData.append('file', file);

    let token = this.authService.getToken();
    if (token && !token.startsWith('Bearer ')) {
      token = `Bearer ${token}`;
    }

    const headers = new HttpHeaders({
      Authorization: token || ''
    });

    return this.http.post<{ file_path: string }>(
      `${environment.apiUrl}/api/upload/coloring`,
      formData,
      { headers }
    );
  }

  uploadStorybookPage(file: File): Observable<{ file_path: string }> {
    const formData = new FormData();
    formData.append('file', file);

    let token = this.authService.getToken();
    if (token && !token.startsWith('Bearer ')) {
      token = `Bearer ${token}`;
    }

    const headers = new HttpHeaders({
      Authorization: token || ''
    });

    return this.http.post<{ file_path: string }>(
      `${environment.apiUrl}/api/upload/storybook`,
      formData,
      { headers }
    );
  }

getCurrentSegment(studentUnitId: string): Observable<SegmentResponse> {
  return this.http.get<SegmentResponse>(
    `${environment.apiUrl}/api/progress/segment?student_unit_id=${studentUnitId}`,
    { headers: this.getHeaders() }
  );
}


  updateCourse(courseId: string, course: CourseDraft): Observable<any> {
    return this.http.put(`${this.apiUrl}/${courseId}`, course, { headers: this.getHeaders() });
  }

  enrollInCourse(courseId: string): Observable<any> {
  const payload = { course_id: courseId };
  return this.http.post(`${environment.apiUrl}/api/enroll`, payload, {
    headers: this.getHeaders()
  });
}


  createCourse(course: CourseDraft): Observable<any> {
    return this.http.post(`${this.apiUrl}`, course, { headers: this.getHeaders() });
  }

   startCourse(request: StartCourseRequest): Observable<SegmentResponse> {
    return this.http.post<SegmentResponse>(this.startCourseUrl, request, {
      headers: this.getHeaders()
    });
  }

  getStudentCourses(): Observable<StudentCourseWithDetails[]> {
  return this.http.get<StudentCourseWithDetails[]>(`${environment.apiUrl}/api/student-courses`, {
    headers: this.getHeaders()
  });
}


  markSegmentCompleted(studentUnitId: string, lessonId: string): Observable<any> {
  const payload = {
    student_unit_id: studentUnitId,
    lesson_id: lessonId
  };

  return this.http.post(`${environment.apiUrl}/api/progress/segment/complete`, payload, {
    headers: this.getHeaders()
  });
  }

  /**
   * Calculate course progress as a percentage based on the current segment
   * returned from the backend. If all segments are completed a value of 100 is returned.
   */
  getCourseProgress(sc: StudentCourseWithDetails): Observable<number> {
    const unitProgressId = sc.unitProgressId;
    const lessons = sc.course.units?.[0]?.lessons || [];
    const total = lessons.length;

    if (!unitProgressId || total === 0) {
      return of(0);
    }

    return this.getCurrentSegment(unitProgressId).pipe(
      map(segment => {
        const index = lessons.findIndex(l => l.id === segment.lesson_id);
        if (index === -1) {
          return 0;
        }
        return (index / total) * 100;
      }),
      catchError(err => {
        // If API returns 404 no segment found => all lessons completed
        if (err.status === 404) {
          return of(100);
        }
        return of(0);
      })
    );
  }

}
