import { Course } from './course';

export interface ContinuationGuidance {
  support_state: 'normal' | 'remediation' | 'enrichment';
  learner_title: string;
  learner_message: string;
  reinforcement_title?: string | null;
  reinforcement_message?: string | null;
  recommended_action: string;
  evidence_source: string;
  review_lesson_id?: string | null;
  review_lesson_title?: string | null;
  review_key_concepts?: string[];
  review_prompts?: string[];
  extension_lesson_id?: string | null;
  extension_lesson_title?: string | null;
  extension_key_concepts?: string[];
  extension_prompts?: string[];
  educator_note?: string | null;
  educator_intervention_hint?: string | null;
}

export interface StudentCourseWithDetails {
  id: string;
  student_id: string;
  course_id: string;
  enrolled_on: string;
  status: string;
  course: Course;
  unit_progress_id?: string;
  continuation_guidance?: ContinuationGuidance | null;
  /** Progress percentage from 0 to 100 */
  progress?: number;
}
