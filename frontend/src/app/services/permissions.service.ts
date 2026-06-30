import { Injectable } from '@angular/core';
import { BehaviorSubject, firstValueFrom } from 'rxjs';
import { AuthService } from './auth.service';
import { OrganizationService } from './organization.service';
import { RoleService } from './role.service';
import { RoleFeatureMap } from '../mappings/role-feature-map';
import { UserInfo } from '../models/user-info';
import { readPendingOrganizationSetup, requiresOrganizationOnboarding } from '../shared/onboarding-flow';

export type BootstrapStatus = 'authenticated' | 'unauthenticated' | 'onboardingRequired' | 'ready' | 'failed';

export interface BootstrapOutcome {
  status: BootstrapStatus;
  authenticated: boolean;
  ready: boolean;
  onboardingRequired: boolean;
  failed: boolean;
  activeOrgId: string | null;
  activeOrgRole: string | null;
  organizations: Array<{ id: string; type?: string; role?: string }>;
  error?: 'invalid_token' | 'expired_token' | 'org_hydration_failed';
}

@Injectable({
  providedIn: 'root'
})
export class PermissionsService {
  private readonly userSubject = new BehaviorSubject<UserInfo | null>(null);
  private readonly permissionsSubject = new BehaviorSubject<Set<string>>(new Set<string>());
  private readonly readySubject = new BehaviorSubject<boolean>(false);
  private readonly outcomeSubject = new BehaviorSubject<BootstrapOutcome>({
    status: 'unauthenticated',
    authenticated: false,
    ready: false,
    onboardingRequired: false,
    failed: false,
    activeOrgId: null,
    activeOrgRole: null,
    organizations: [],
  });
  private bootstrapPromise: Promise<void> | null = null;

  readonly user$ = this.userSubject.asObservable();
  readonly permissions$ = this.permissionsSubject.asObservable();
  readonly ready$ = this.readySubject.asObservable();
  readonly outcome$ = this.outcomeSubject.asObservable();

  constructor(
    private authService: AuthService,
    private organizationService: OrganizationService,
    private roleService: RoleService,
  ) {}

  async bootstrapSession(): Promise<void> {
    if (this.readySubject.value) {
      return;
    }

    if (this.bootstrapPromise) {
      return this.bootstrapPromise;
    }

    this.bootstrapPromise = this.loadSession();
    try {
      await this.bootstrapPromise;
    } finally {
      this.bootstrapPromise = null;
    }
  }


  async refreshSession(): Promise<void> {
    this.readySubject.next(false);
    this.bootstrapPromise = this.loadSession();
    try {
      await this.bootstrapPromise;
    } finally {
      this.bootstrapPromise = null;
    }
  }

  hasPermission(permission: string): boolean {
    return this.permissionsSubject.value.has(permission);
  }

  hasAnyRole(...rolesToCheck: string[]): boolean {
    const permissions = this.permissionsSubject.value;
    return rolesToCheck.some(role => permissions.has(`role:${role}`));
  }

  getCurrentOutcome(): BootstrapOutcome {
    return this.outcomeSubject.value;
  }

  resetSession(): void {
    this.userSubject.next(null);
    this.permissionsSubject.next(new Set<string>());
    this.readySubject.next(false);
    this.roleService.setUserRoles([]);
    this.outcomeSubject.next({
      status: 'unauthenticated',
      authenticated: false,
      ready: false,
      onboardingRequired: false,
      failed: false,
      activeOrgId: null,
      activeOrgRole: null,
      organizations: [],
    });
  }

  private async loadSession(): Promise<void> {
    const token = this.authService.getToken();
    if (!token) {
      this.resetSession();
      return;
    }

    const user = this.authService.getTokenPayload(token) as UserInfo | null;
    if (!user) {
      this.resetSessionWithError('invalid_token');
      return;
    }

    if (this.authService.isTokenExpired(token)) {
      this.resetSessionWithError('expired_token');
      return;
    }

    this.readySubject.next(false);
    this.userSubject.next(user);
    this.outcomeSubject.next({
      status: 'authenticated',
      authenticated: true,
      ready: false,
      onboardingRequired: false,
      failed: false,
      activeOrgId: this.organizationService.getActiveOrgId(),
      activeOrgRole: this.organizationService.getActiveOrgRole(),
      organizations: this.organizationService.organizationsSubjectValue,
    });

    let orgs = this.organizationService.organizationsSubjectValue;
    if (orgs.length === 0) {
      try {
        orgs = await firstValueFrom(this.organizationService.refreshOrganizations());
      } catch {
        this.roleService.setUserRoles([]);
        this.permissionsSubject.next(new Set<string>());
        this.readySubject.next(false);
        this.outcomeSubject.next({
          status: 'failed',
          authenticated: true,
          ready: false,
          onboardingRequired: false,
          failed: true,
          activeOrgId: this.organizationService.getActiveOrgId(),
          activeOrgRole: this.organizationService.getActiveOrgRole(),
          organizations: [],
          error: 'org_hydration_failed',
        });
        return;
      }
    }

    const onboardingRequired = requiresOrganizationOnboarding({
      isSuperAdmin: this.authService.isSuperAdminRole(user.role),
      organizations: orgs,
      pendingSetup: readPendingOrganizationSetup(),
    });

    const roles = this.resolveRoles(user, orgs);
    const permissions = this.buildPermissions(roles);
    const activeOrgId = this.organizationService.getActiveOrgId();
    const activeOrgRole = this.resolveActiveOrgRole(orgs);

    this.roleService.setUserRoles(roles);
    // Emit a fresh Set reference so OnPush consumers update immediately.
    this.permissionsSubject.next(new Set<string>(permissions));
    this.readySubject.next(true);
    this.outcomeSubject.next({
      status: onboardingRequired ? 'onboardingRequired' : 'ready',
      authenticated: true,
      ready: true,
      onboardingRequired,
      failed: false,
      activeOrgId,
      activeOrgRole,
      organizations: orgs,
    });
  }

  private resolveRoles(user: UserInfo, organizations: Array<{ id: string; role?: string }>): string[] {
    const allRoles = new Set<string>();
    if (user.role) {
      allRoles.add(user.role);
    }

    const activeOrgRole = this.resolveActiveOrgRole(organizations);
    if (activeOrgRole) {
      allRoles.add(activeOrgRole);
    }

    const activeOrgId = this.organizationService.getActiveOrgId();
    if (!activeOrgRole && activeOrgId) {
      const matchingOrg = organizations.find(org => org.id === activeOrgId);
      if (matchingOrg?.role) {
        allRoles.add(matchingOrg.role);
      }
    }

    return Array.from(allRoles);
  }

  private resolveActiveOrgRole(organizations: Array<{ id: string; role?: string }>): string | null {
    const storedActiveOrgRole = this.organizationService.getActiveOrgRole();
    if (storedActiveOrgRole) {
      return storedActiveOrgRole;
    }

    const activeOrgId = this.organizationService.getActiveOrgId();
    if (!activeOrgId) {
      return null;
    }

    const matchingOrg = organizations.find(org => org.id === activeOrgId);
    return matchingOrg?.role ?? null;
  }

  private buildPermissions(roles: string[]): Set<string> {
    const roleSet = new Set(roles);
    const permissions = new Set<string>();

    roles.forEach(role => permissions.add(`role:${role}`));

    Object.entries(RoleFeatureMap).forEach(([feature, allowedRoles]) => {
      if (allowedRoles.some(role => roleSet.has(role))) {
        permissions.add(`feature:${feature}`);
      }
    });

    permissions.add('nav:dashboard');
    permissions.add('nav:courses');
    permissions.add('nav:programs');
    permissions.add('nav:certifications');
    permissions.add('nav:preferences');
    permissions.add('nav:workspace');
    permissions.add('nav:products');
    permissions.add('nav:learners');
    permissions.add('nav:settings');

    if (this.hasRole(roleSet, ['admin', 'teacher', 'content_admin', 'org_admin', 'instructor'])) {
      permissions.add('nav:projects');
      permissions.add('nav:product-studio');
      permissions.add('nav:knowledge-sources');
      permissions.add('nav:artifacts');
      permissions.add('nav:review-center');
      permissions.add('nav:analytics');
    }

    if (this.hasRole(roleSet, ['admin'])) {
      permissions.add('nav:admin-badges');
      permissions.add('nav:admin-users');
      permissions.add('nav:admin-courses');
    }

    if (this.hasRole(roleSet, ['org_admin', 'content_admin'])) {
      permissions.add('nav:org-invites');
      permissions.add('nav:studio-courses');
    }

    if (this.hasRole(roleSet, ['teacher', 'org_admin', 'instructor'])) {
      permissions.add('nav:sections');
      permissions.add('nav:cohorts');
    }

    return permissions;
  }

  private hasRole(roleSet: Set<string>, roles: string[]): boolean {
    return roles.some(role => roleSet.has(role));
  }

  private resetSessionWithError(error: 'invalid_token' | 'expired_token'): void {
    this.userSubject.next(null);
    this.permissionsSubject.next(new Set<string>());
    this.readySubject.next(false);
    this.roleService.setUserRoles([]);
    this.outcomeSubject.next({
      status: 'unauthenticated',
      authenticated: false,
      ready: false,
      onboardingRequired: false,
      failed: false,
      activeOrgId: null,
      activeOrgRole: null,
      organizations: [],
      error,
    });
  }
}
