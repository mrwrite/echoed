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
