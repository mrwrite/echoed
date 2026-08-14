export interface AuditEvent {
  id: string;
  created_at: string;
  schema_version: number;
  actor_id?: string | null;
  actor_role: string;
  action: string;
  category: string;
  outcome: string;
  target_type: string;
  target_id: string;
  organization_id?: string | null;
  request_id?: string | null;
  correlation_id?: string | null;
  reason_code?: string | null;
  before_state: Record<string, string | number | boolean | null>;
  after_state: Record<string, string | number | boolean | null>;
  integrity_verified: boolean;
}

export interface AuditEventPage {
  items: AuditEvent[];
  next_cursor?: string | null;
}

export interface AuditEventFilters {
  action?: string;
  category?: string;
  outcome?: string;
  cursor?: string;
  limit?: number;
}
