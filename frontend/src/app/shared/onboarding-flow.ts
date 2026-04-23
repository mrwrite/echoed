import { Organization } from '../models/organization';

export const PENDING_ORG_CREATION_KEY = 'pending_org_creation';

export interface PendingOrganizationSetup {
  name: string;
  type: string;
}

export function normalizePendingOrganizationSetup(input: {
  createOrganization?: boolean | null;
  organizationName?: string | null;
  organizationType?: string | null;
}): PendingOrganizationSetup | null {
  if (!input.createOrganization) {
    return null;
  }

  const name = input.organizationName?.trim() ?? '';
  const type = input.organizationType?.trim().toLowerCase() ?? '';

  if (!name || !type) {
    return null;
  }

  return {
    name,
    type,
  };
}

export function readPendingOrganizationSetup(storage: Storage = sessionStorage): PendingOrganizationSetup | null {
  const rawValue = storage.getItem(PENDING_ORG_CREATION_KEY);
  if (!rawValue) {
    return null;
  }

  try {
    const parsed = JSON.parse(rawValue) as Partial<PendingOrganizationSetup> | null;
    const normalized = normalizePendingOrganizationSetup({
      createOrganization: true,
      organizationName: parsed?.name ?? '',
      organizationType: parsed?.type ?? '',
    });

    if (!normalized) {
      storage.removeItem(PENDING_ORG_CREATION_KEY);
      return null;
    }

    return normalized;
  } catch {
    storage.removeItem(PENDING_ORG_CREATION_KEY);
    return null;
  }
}

export function writePendingOrganizationSetup(
  pendingSetup: PendingOrganizationSetup | null,
  storage: Storage = sessionStorage,
): void {
  if (!pendingSetup) {
    storage.removeItem(PENDING_ORG_CREATION_KEY);
    return;
  }

  storage.setItem(PENDING_ORG_CREATION_KEY, JSON.stringify(pendingSetup));
}

export function clearPendingOrganizationSetup(storage: Storage = sessionStorage): void {
  storage.removeItem(PENDING_ORG_CREATION_KEY);
}

export function requiresOrganizationOnboarding(input: {
  isSuperAdmin: boolean;
  organizations: Organization[] | null | undefined;
  pendingSetup?: PendingOrganizationSetup | null;
}): boolean {
  if (input.isSuperAdmin) {
    return false;
  }

  if (input.pendingSetup) {
    return true;
  }

  const organizations = input.organizations ?? [];
  if (organizations.length === 0) {
    return true;
  }

  return !organizations.some((organization) => organization.type !== 'personal');
}
