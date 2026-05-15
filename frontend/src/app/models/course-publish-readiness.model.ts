export interface PublishReadinessIssue {
  entity_type: string;
  entity_id?: string | null;
  entity_title: string;
  code: string;
  message: string;
}

export interface CoursePublishReadiness {
  course_id: string;
  course_title: string;
  is_ready: boolean;
  blocking_issue_count: number;
  warning_count: number;
  blocking_issues: PublishReadinessIssue[];
  warnings: PublishReadinessIssue[];
}

export interface CourseSafePublishValidation {
  course_id: string;
  course_title: string;
  is_safe: boolean;
  blocking_issue_count: number;
  warning_count: number;
  blocking_issues: PublishReadinessIssue[];
  warnings: PublishReadinessIssue[];
}

export interface CompetencyEvidenceAffectedAssessment {
  assessment_id?: string | null;
  assessment_title: string;
  competency_identifiers: string[];
}

export interface CourseCompetencyEvidenceIntegrity {
  course_id: string;
  course_title: string;
  is_valid: boolean;
  is_explainable: boolean;
  blocking_issue_count: number;
  warning_count: number;
  blocking_issues: PublishReadinessIssue[];
  warnings: PublishReadinessIssue[];
  affected_assessments: CompetencyEvidenceAffectedAssessment[];
  affected_competency_identifiers: string[];
}

export interface RuntimeInterventionEvidenceBasis {
  source: string;
  detail: string;
  assessment_id?: string | null;
  assessment_title?: string | null;
  competency_identifiers: string[];
}

export interface CourseRuntimeInterventionRecommendation {
  student_id: string;
  student_name: string;
  student_course_id: string;
  course_id: string;
  course_title: string;
  recommendation_state: string;
  educator_attention_level: string;
  summary: string;
  evidence_basis: RuntimeInterventionEvidenceBasis[];
  confidence_level: string;
  caution_flags: string[];
  learner_safe_message: string;
}
