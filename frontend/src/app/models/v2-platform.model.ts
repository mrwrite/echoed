export interface Workspace {
  id: string;
  organization_id?: string | null;
  name: string;
  slug?: string | null;
  description?: string | null;
  status: string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: string;
  workspace_id: string;
  name: string;
  description?: string | null;
  status: string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Product {
  id: string;
  workspace_id: string;
  project_id?: string | null;
  course_id?: string | null;
  program_id?: string | null;
  product_type: string;
  title: string;
  description?: string | null;
  status: string;
  review_state: string;
  access_state: string;
  metadata: Record<string, unknown>;
  published_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface KnowledgeSource {
  id: string;
  workspace_id: string;
  project_id: string;
  source_id?: string | null;
  title: string;
  source_type: string;
  uri?: string | null;
  citation?: string | null;
  content_hash?: string | null;
  status: string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Artifact {
  id: string;
  workspace_id: string;
  project_id: string;
  product_id?: string | null;
  generation_run_id?: string | null;
  knowledge_source_id?: string | null;
  artifact_type: string;
  title: string;
  body?: string | null;
  uri?: string | null;
  status: string;
  review_state: string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface GenerationRun {
  id: string;
  workspace_id: string;
  project_id: string;
  product_id?: string | null;
  status: string;
  provider?: string | null;
  model_name?: string | null;
  prompt?: string | null;
  output_summary?: string | null;
  input_metadata: Record<string, unknown>;
  output_metadata: Record<string, unknown>;
  error_message?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  created_at: string;
}

export interface ProjectCreateRequest {
  workspace_id: string;
  name: string;
  description?: string | null;
  status?: string;
  metadata?: Record<string, unknown>;
}

export interface ProductCreateRequest {
  workspace_id: string;
  project_id?: string | null;
  course_id?: string | null;
  program_id?: string | null;
  product_type: string;
  title: string;
  description?: string | null;
  status?: string;
  review_state?: string;
  access_state?: string;
  metadata?: Record<string, unknown>;
}

export interface KnowledgeSourceCreateRequest {
  workspace_id: string;
  project_id: string;
  source_id?: string | null;
  title: string;
  source_type: string;
  uri?: string | null;
  citation?: string | null;
  content_hash?: string | null;
  status?: string;
  metadata?: Record<string, unknown>;
}

export interface ArtifactCreateRequest {
  workspace_id: string;
  project_id: string;
  product_id?: string | null;
  generation_run_id?: string | null;
  knowledge_source_id?: string | null;
  artifact_type: string;
  title: string;
  body?: string | null;
  uri?: string | null;
  status?: string;
  review_state?: string;
  metadata?: Record<string, unknown>;
}
