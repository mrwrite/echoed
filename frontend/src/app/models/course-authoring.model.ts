export interface CourseAuthoringCapabilities {
  can_create: boolean;
  can_view_draft: boolean;
  can_edit: boolean;
  can_duplicate: boolean;
  can_preview: boolean;
  can_submit_review: boolean;
  can_review: boolean;
  can_publish: boolean;
}

export interface CourseAuthoringCapabilityEnvelope {
  organization_id?: string | null;
  course_id?: string | null;
  capabilities: CourseAuthoringCapabilities;
}

export interface AuthoringStorybookPage {
  id?: string;
  image_url: string;
  order?: number;
}

export interface AuthoringActivity {
  id?: string;
  type: string;
  title: string;
  content: string;
  order?: number;
  media_id?: string | null;
  pages: AuthoringStorybookPage[];
}

export interface AuthoringSource {
  id?: string;
  citation: string;
  url?: string | null;
}

export interface AuthoringLesson {
  id?: string;
  title: string;
  objective?: string | null;
  learning_objectives?: string | null;
  key_concepts: string[];
  teacher_notes?: string | null;
  discussion_questions: string[];
  hook?: string | null;
  content?: string | null;
  guided_practice?: string | null;
  independent_practice?: string | null;
  assessment?: string | null;
  skill_tags: string[];
  standards_metadata: Record<string, unknown>;
  order?: number;
  duration_minutes?: number | null;
  activities: AuthoringActivity[];
  sources: AuthoringSource[];
  assessment_ids?: string[];
}

export interface AuthoringUnit {
  id?: string;
  title: string;
  content?: string | null;
  order?: number;
  lessons: AuthoringLesson[];
  assessment_ids?: string[];
}

export interface CourseAuthoringDraft {
  id?: string;
  title: string;
  description: string;
  subject?: string | null;
  age_band_min?: number | null;
  age_band_max?: number | null;
  default_locale: string;
  learning_objectives?: string | null;
  skill_tags: string[];
  standards_metadata: Record<string, unknown>;
  organization_id?: string | null;
  created_by?: string | null;
  revision_number?: number;
  revision_status?: string;
  revision_metadata?: Record<string, unknown>;
  updated_at?: string;
  current_version_id?: string | null;
  units: AuthoringUnit[];
  assessment_ids?: string[];
  capabilities?: CourseAuthoringCapabilities;
  template_id?: string | null;
}

export interface CourseAuthoringValidationIssue {
  severity: 'blocking' | 'warning' | 'recommendation';
  entity_type: string;
  entity_id?: string | null;
  field: string;
  message: string;
  corrective_context: string;
}

export interface CourseAuthoringConflict {
  code: 'course_authoring_revision_conflict';
  course_id: string;
  current_revision: number;
  updated_at?: string | null;
}

export interface CourseLifecycleResponse {
  course_id: string;
  lifecycle_state: string;
  revision_number: number;
  version_id?: string | null;
  feedback?: string | null;
  changed_at: string;
}

export interface CourseVersionSummary {
  id: string;
  course_id: string;
  version_number: number;
  status: string;
  changelog?: string | null;
  created_at: string;
  published_at?: string | null;
  published_by?: string | null;
}

export interface CourseTemplate {
  id: string;
  name: string;
  description: string;
  course: Partial<CourseAuthoringDraft>;
}

export type CourseStudioMode = 'setup' | 'build' | 'quality' | 'preview' | 'release';
export type CourseSaveState = 'idle' | 'dirty' | 'saving' | 'saved' | 'failed' | 'offline' | 'conflict';

export function emptyCourseAuthoringDraft(): CourseAuthoringDraft {
  return {
    title: '',
    description: '',
    subject: null,
    age_band_min: null,
    age_band_max: null,
    default_locale: 'en',
    learning_objectives: null,
    skill_tags: [],
    standards_metadata: {},
    units: [],
  };
}
