import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface AdminOverviewResponse {
  totals: {
    students: number;
    teachers: number;
    courses: number;
    active_students: number;
    total_enrollments: number;
    pending_enrollments: number;
  };
  progress: {
    lessons_completed: number;
    units_completed: number;
    courses_completed: number;
    course_completion_rate: number;
  };
}

export interface TeacherSummaryRow {
  student_name: string;
  course_title: string;
  progress: number;
  last_active: string | null;
  status: string;
}

export interface StudentProgressResponse {
  metrics: {
    lessons_completed: number;
    units_completed: number;
    courses_completed: number;
    streak_days: number;
  };
  badge_progress: {
    title: string;
    description: string;
    current: number;
    target: number;
    earned: boolean;
  }[];
}

export type EducatorRuntimeSupportState =
  | 'normal'
  | 'remediation'
  | 'enrichment'
  | 'completed'
  | 'unknown';

export interface EducatorRuntimeSupportSummary {
  student_id: string;
  student_name: string;
  student_course_id: string;
  course_id: string;
  course_title: string;
  support_state: EducatorRuntimeSupportState;
  support_summary: string;
  evidence_source: string;
  recommended_action: string;
  last_evidence_at: string | null;
  context_lesson_id: string | null;
  context_lesson_title: string | null;
  context_key_concepts: string[];
  context_prompts: string[];
  educator_intervention_hint: string | null;
}

@Injectable({ providedIn: 'root' })
export class AnalyticsService {
  private apiUrl = `${environment.apiUrl}/api/analytics`;

  constructor(private http: HttpClient) {}

  getAdminOverview(): Observable<AdminOverviewResponse> {
    return this.http.get<AdminOverviewResponse>(`${this.apiUrl}/overview`);
  }

  getTeacherSummary(): Observable<TeacherSummaryRow[]> {
    return this.http.get<TeacherSummaryRow[]>(`${this.apiUrl}/teacher-summary`);
  }

  getEducatorRuntimeSupport(courseId: string): Observable<EducatorRuntimeSupportSummary[]> {
    return this.http.get<EducatorRuntimeSupportSummary[]>(
      `${this.apiUrl}/educator-runtime-support?course_id=${courseId}`
    );
  }

  getStudentProgress(): Observable<StudentProgressResponse> {
    return this.http.get<StudentProgressResponse>(`${this.apiUrl}/student-progress`);
  }
}
