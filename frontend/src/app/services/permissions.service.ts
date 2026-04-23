import { Injectable } from '@angular/core';
import { BehaviorSubject, firstValueFrom } from 'rxjs';
import { AuthService } from './auth.service';
import { OrganizationService } from './organization.service';
import { RoleService } from './role.service';
import { RoleFeatureMap } from '../mappings/role-feature-map';
import { UserInfo } from '../models/user-info';

@Injectable({
  providedIn: 'root'
})
export class PermissionsService {
  private readonly userSubject = new BehaviorSubject<UserInfo | null>(null);
  private readonly permissionsSubject = new BehaviorSubject<Set<string>>(new Set<string>());
  private readonly readySubject = new BehaviorSubject<boolean>(false);
  private bootstrapPromise: Promise<void> | null = null;

  readonly user$ = this.userSubject.asObservable();
  readonly permissions$ = this.permissionsSubject.asObservable();
  readonly ready$ = this.readySubject.asObservable();

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

  resetSession(): void {
    this.userSubject.next(null);
    this.permissionsSubject.next(new Set<string>());
    this.readySubject.next(false);
    this.roleService.setUserRoles([]);
  }

  private async loadSession(): Promise<void> {
    const token = this.authService.getToken();
    if (!token) {
      this.resetSession();
      return;
    }

    const user = this.authService.getTokenPayload(token) as UserInfo | null;
    if (!user) {
      this.resetSession();
      return;
    }

    this.readySubject.next(false);

    let orgs = this.organizationService.organizationsSubjectValue;
    if (orgs.length === 0) {
      try {
        orgs = await firstValueFrom(this.organizationService.refreshOrganizations());
      } catch {
        orgs = [];
      }
    }

    const roles = this.resolveRoles(user, orgs);
    const permissions = this.buildPermissions(roles);

    this.roleService.setUserRoles(roles);
    this.userSubject.next(user);
    // Emit a fresh Set reference so OnPush consumers update immediately.
    this.permissionsSubject.next(new Set<string>(permissions));
    this.readySubject.next(true);
  }

  private resolveRoles(user: UserInfo, organizations: Array<{ id: string; role?: string }>): string[] {
    const allRoles = new Set<string>();
    if (user.role) {
      allRoles.add(user.role);
    }

    const activeOrgRole = this.organizationService.getActiveOrgRole();
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
    }

    return permissions;
  }

  private hasRole(roleSet: Set<string>, roles: string[]): boolean {
    return roles.some(role => roleSet.has(role));
  }
}
