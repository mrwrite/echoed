import { HttpClient } from '@angular/common/http';
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

@Injectable({
  providedIn: 'root'
})
export class ProgramsService {
  private readonly apiUrl = `${environment.apiUrl}/api`;

  constructor(private http: HttpClient) {}

  getPrograms(): Observable<Program[]> {
    return this.http.get<Program[]>(`${this.apiUrl}/programs`);
  }

  getProgram(programId: string): Observable<Program> {
    return this.http.get<Program>(`${this.apiUrl}/programs/${programId}`);
  }

  enrollInProgram(programId: string): Observable<StudentProgramProgress> {
    return this.http.post<StudentProgramProgress>(`${this.apiUrl}/programs/${programId}/enroll`, {});
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
    return this.http.get<Assessment[]>(url);
  }

  getAssessment(assessmentId: string): Observable<Assessment> {
    return this.http.get<Assessment>(`${this.apiUrl}/assessments/${assessmentId}`);
  }

  submitAssessment(assessmentId: string, answers: Array<{ question_id: string; answer: string }>): Observable<AssessmentAttemptResult> {
    return this.http.post<AssessmentAttemptResult>(
      `${this.apiUrl}/assessments/${assessmentId}/attempts`,
      { answers }
    );
  }

  getCertifications(programId?: string): Observable<Certification[]> {
    const url = programId
      ? `${this.apiUrl}/certifications?program_id=${programId}`
      : `${this.apiUrl}/certifications`;
    return this.http.get<Certification[]>(url);
  }

  evaluateCertification(certificationId: string): Observable<CertificationEvaluationResult> {
    return this.http.post<CertificationEvaluationResult>(
      `${this.apiUrl}/certifications/${certificationId}/evaluate`,
      {}
    );
  }

  getMyCertifications(): Observable<StudentCertification[]> {
    return this.http.get<StudentCertification[]>(`${this.apiUrl}/students/me/certifications`);
  }
}
