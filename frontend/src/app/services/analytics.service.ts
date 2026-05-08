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

  getStudentProgress(): Observable<StudentProgressResponse> {
    return this.http.get<StudentProgressResponse>(`${this.apiUrl}/student-progress`);
  }
}
