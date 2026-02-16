import { Injectable } from '@angular/core';
import { RoleFeatureMap } from '../mappings/role-feature-map';

@Injectable({
  providedIn: 'root'
})
export class RoleService {
  private userRoles: string[] = [];

  setUserRoles(roles: string[]): void {
    this.userRoles = [...roles];
  }

  hasAccess(feature: string): boolean {
    const allowedRoles = RoleFeatureMap[feature] || [];
    return this.userRoles.some(role => allowedRoles.includes(role));
  }

  hasAnyRole(...rolesToCheck: string[]): boolean {
    return this.userRoles.some(role => rolesToCheck.includes(role));
  }

  getUserRoles(): string[] {
    return [...this.userRoles];
  }
}
