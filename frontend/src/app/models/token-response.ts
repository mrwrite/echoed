export interface ActiveOrganizationContextResponse {
    id: string;
    name: string;
    type: string;
    role: string;
}

export interface TokenResponse {
    access_token: string;
    token_type: string;
    organizations?: { id: string; role: string }[];
    active_org_id?: string | null;
    active_org_role?: string | null;
    active_organization?: ActiveOrganizationContextResponse | null;
}
