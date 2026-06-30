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

export interface V2AnalyticsRecentItem {
  id: string;
  item_type: string;
  title: string;
  status: string;
  subtype?: string | null;
  created_at: string | null;
}

export interface V2WorkspaceAnalytics {
  totals: {
    total_products: number;
    total_projects: number;
    total_knowledge_sources: number;
    total_artifacts: number;
    total_generation_runs: number;
    total_access_grants: number;
    learner_count: number;
    enrollment_count: number;
    course_backed_product_count: number;
    program_backed_product_count: number;
  };
  products_by_type: Record<string, number>;
  products_by_status: Record<string, number>;
  artifacts_by_status: Record<string, number>;
  artifacts_by_type: Record<string, number>;
  generation_runs_by_status: Record<string, number>;
  access_grants_by_status: Record<string, number>;
  access_grants_by_type: Record<string, number>;
  review_health: Record<string, number>;
  learner_engagement: Record<string, number>;
  recent: {
    products: V2AnalyticsRecentItem[];
    artifacts: V2AnalyticsRecentItem[];
    knowledge_sources: V2AnalyticsRecentItem[];
  };
  event_tracking: {
    status: string;
    message: string;
  };
  scoped_product_count: number;
}

export interface V2ProductAnalytics {
  total_products: number;
  course_backed_product_count: number;
  program_backed_product_count: number;
  products_by_type: Record<string, number>;
  products_by_status: Record<string, number>;
  products: {
    id: string;
    title: string;
    product_type: string;
    status: string;
    review_state: string;
    access_state: string;
    course_id?: string | null;
    program_id?: string | null;
    artifact_count: number;
    generation_run_count: number;
    access_grant_count: number;
    enrollment_count: number;
    created_at: string | null;
    updated_at: string | null;
  }[];
}

export interface V2LearnerAnalytics {
  summary: Record<string, number>;
  enrollments_by_status: Record<string, number>;
  access_grants_by_status: Record<string, number>;
  access_grants_by_type: Record<string, number>;
}

export interface V2KnowledgePipelineAnalytics {
  total_projects: number;
  total_knowledge_sources: number;
  total_artifacts: number;
  total_generation_runs: number;
  knowledge_sources_by_type: Record<string, number>;
  knowledge_sources_by_status: Record<string, number>;
  artifacts_by_status: Record<string, number>;
  artifacts_by_type: Record<string, number>;
  generation_runs_by_status: Record<string, number>;
  recent: {
    artifacts: V2AnalyticsRecentItem[];
    knowledge_sources: V2AnalyticsRecentItem[];
  };
  source_coverage: Record<string, number | string>;
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

  getV2WorkspaceAnalytics(): Observable<V2WorkspaceAnalytics> {
    return this.http.get<V2WorkspaceAnalytics>(`${this.apiUrl}/workspace`);
  }

  getV2ProductAnalytics(): Observable<V2ProductAnalytics> {
    return this.http.get<V2ProductAnalytics>(`${this.apiUrl}/products`);
  }

  getV2LearnerAnalytics(): Observable<V2LearnerAnalytics> {
    return this.http.get<V2LearnerAnalytics>(`${this.apiUrl}/learners`);
  }

  getV2KnowledgePipelineAnalytics(): Observable<V2KnowledgePipelineAnalytics> {
    return this.http.get<V2KnowledgePipelineAnalytics>(`${this.apiUrl}/knowledge-pipeline`);
  }
}
