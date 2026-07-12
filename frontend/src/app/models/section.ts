export interface Section {
  id: string;
  organization_id: string;
  course_version_id: string;
  name: string;
  mode: string;
  start_date?: string | null;
  end_date?: string | null;
  created_by: string;
}

export interface Assignment {
  id: string;
  section_id: string;
  target_type: string;
  target_id: string;
  due_at?: string | null;
  instructions?: string | null;
  created_by: string;
  created_at: string;
}

export interface Enrollment {
  id: string;
  section_id: string;
  user_id: string;
  role_in_section: string;
  status: string;
  enrolled_at: string;
}

export interface SectionSummary {
  section_id: string;
  totals: {
    enrolled: number;
    lessons_completed: number;
    units_completed: number;
  };
}
