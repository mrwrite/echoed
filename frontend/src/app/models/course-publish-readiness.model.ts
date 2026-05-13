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
