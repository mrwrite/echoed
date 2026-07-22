export interface Organization {
  id: string;
  name: string;
  type: string;
  country?: string;
  timezone?: string;
  created_at?: string;
  role?: string;
}

export interface OrganizationInvite {
  id: string;
  organization_id: string;
  email: string;
  role: string;
  token: string;
  expires_at: string;
  accepted_at?: string | null;
  invited_by_user_id: string;
}

export interface OrganizationMembershipSummary {
  id: string;
  role: string;
}

export interface OrganizationMember {
  id: string;
  user_id: string;
  display_name: string;
  username: string;
  role: string;
  status: string;
  joined_at: string;
}
