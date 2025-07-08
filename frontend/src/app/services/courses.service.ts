import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';
import { environment } from '../../environments/environment';
import { Course } from '../models/course';
import { CourseDto } from '../models/course-dto';
import { CourseDraft } from '../pages/admin/course-wizard/models/course-draft.model';
import { StartCourseRequest, SegmentResponse } from '../models/segment-response.model';
import { Lesson } from '../models/lesson';
import { StudentCourse } from '../models/student-course';
import { StudentCourseWithDetails } from '../models/student-course-with-details.model';

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

getCurrentSegment(studentUnitId: string): Observable<SegmentResponse> {
  return this.http.get<SegmentResponse>(
    `${environment.apiUrl}/api/segment?student_unit_id=${studentUnitId}`,
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

  return this.http.post(`${environment.apiUrl}/api/complete-segment`, payload, {
    headers: this.getHeaders()
  });
}

}
