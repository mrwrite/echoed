export interface TokenResponse {
    access_token: string;
    token_type: string;
    organizations?: { id: string; role: string }[];
    active_org_id?: string | null;
  }
