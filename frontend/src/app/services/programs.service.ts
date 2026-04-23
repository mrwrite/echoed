import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import {
  Assessment,
  AssessmentAttemptResult,
  Certification,
  CertificationEvaluationResult,
  Program,
  StudentCertification,
  StudentProgramProgress,
} from '../models/program';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class ProgramsService {
  private readonly apiUrl = `${environment.apiUrl}/api`;

  constructor(private http: HttpClient, private authService: AuthService) {}

  private getHeaders(): HttpHeaders {
    let token = this.authService.getToken();
    if (token && !token.startsWith('Bearer ')) {
      token = `Bearer ${token}`;
    }
    return new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: token || ''
    });
  }

  getPrograms(): Observable<Program[]> {
    return this.http.get<Program[]>(`${this.apiUrl}/programs`, { headers: this.getHeaders() });
  }

  getProgram(programId: string): Observable<Program> {
    return this.http.get<Program>(`${this.apiUrl}/programs/${programId}`, { headers: this.getHeaders() });
  }

  enrollInProgram(programId: string): Observable<StudentProgramProgress> {
    return this.http.post<StudentProgramProgress>(`${this.apiUrl}/programs/${programId}/enroll`, {}, { headers: this.getHeaders() });
  }

  getAssessments(params?: { lessonId?: string; courseId?: string; programId?: string }): Observable<Assessment[]> {
    const search = new URLSearchParams();
    if (params?.lessonId) {
      search.set('lesson_id', params.lessonId);
    }
    if (params?.courseId) {
      search.set('course_id', params.courseId);
    }
    if (params?.programId) {
      search.set('program_id', params.programId);
    }
    const query = search.toString();
    const url = query ? `${this.apiUrl}/assessments?${query}` : `${this.apiUrl}/assessments`;
    return this.http.get<Assessment[]>(url, { headers: this.getHeaders() });
  }

  getAssessment(assessmentId: string): Observable<Assessment> {
    return this.http.get<Assessment>(`${this.apiUrl}/assessments/${assessmentId}`, { headers: this.getHeaders() });
  }

  submitAssessment(assessmentId: string, answers: Array<{ question_id: string; answer: string }>): Observable<AssessmentAttemptResult> {
    return this.http.post<AssessmentAttemptResult>(
      `${this.apiUrl}/assessments/${assessmentId}/attempts`,
      { answers },
      { headers: this.getHeaders() }
    );
  }

  getCertifications(programId?: string): Observable<Certification[]> {
    const url = programId
      ? `${this.apiUrl}/certifications?program_id=${programId}`
      : `${this.apiUrl}/certifications`;
    return this.http.get<Certification[]>(url, { headers: this.getHeaders() });
  }

  evaluateCertification(certificationId: string): Observable<CertificationEvaluationResult> {
    return this.http.post<CertificationEvaluationResult>(
      `${this.apiUrl}/certifications/${certificationId}/evaluate`,
      {},
      { headers: this.getHeaders() }
    );
  }

  getMyCertifications(): Observable<StudentCertification[]> {
    return this.http.get<StudentCertification[]>(`${this.apiUrl}/students/me/certifications`, { headers: this.getHeaders() });
  }
}
