import { Course } from './course';

export interface ProgramCourseLink {
  id: string;
  course_id: string;
  order: number;
  is_required: boolean;
  course: Course;
}

export interface StudentProgramProgress {
  id: string;
  student_id: string;
  program_id: string;
  status: string;
  enrolled_on: string;
  last_activity_at?: string | null;
  completed_at?: string | null;
  completion_percentage: number;
  completed_courses: number;
  total_courses: number;
}

export interface Program {
  id: string;
  title: string;
  description: string;
  organization_id?: string | null;
  created_by?: string | null;
  created_at: string;
  updated_at: string;
  courses: ProgramCourseLink[];
  progress?: StudentProgramProgress | null;
}

export interface Question {
  id: string;
  prompt: string;
  question_type: string;
  choices: string[];
  explanation?: string | null;
  points: number;
  order: number;
}

export interface Assessment {
  id: string;
  title: string;
  description?: string | null;
  lesson_id?: string | null;
  course_id?: string | null;
  program_id?: string | null;
  passing_score: number;
  max_attempts?: number | null;
  created_by?: string | null;
  created_at: string;
  questions: Question[];
}

export interface AssessmentAnswerResult {
  question_id: string;
  answer: string;
  is_correct: boolean;
  awarded_points: number;
}

export interface AssessmentAttemptResult {
  id: string;
  assessment_id: string;
  student_id: string;
  program_progress_id?: string | null;
  score: number;
  max_score: number;
  percentage: number;
  passed: boolean;
  submitted_at: string;
  answers: AssessmentAnswerResult[];
}

export interface CertificationRequirement {
  id: string;
  requirement_type: string;
  course_id?: string | null;
  assessment_id?: string | null;
  minimum_score?: number | null;
}

export interface Certification {
  id: string;
  program_id: string;
  badge_id?: string | null;
  title: string;
  description?: string | null;
  created_at: string;
  requirements: CertificationRequirement[];
}

export interface StudentCertification {
  id: string;
  student_id: string;
  certification_id: string;
  awarded_at: string;
  score_snapshot?: number | null;
  certification: Certification;
}

export interface CertificationEvaluationResult {
  certification_id: string;
  awarded: boolean;
  missing_requirements: string[];
  student_certification?: StudentCertification | null;
}
