import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Organization } from '../models/organization';

@Injectable({
  providedIn: 'root'
})
export class OrganizationService {
  private apiUrl = `${environment.apiUrl}/api`;
  private activeOrgKey = 'active_org_id';
  private activeOrgRoleKey = 'active_org_role';
  private activeOrgSubject = new BehaviorSubject<string | null>(this.getActiveOrgId());

  activeOrg$ = this.activeOrgSubject.asObservable();

  constructor(private http: HttpClient) {}

  getOrganizations(): Observable<Organization[]> {
    return this.http.get<Organization[]>(`${this.apiUrl}/orgs`);
  }

  getActiveOrgId(): string | null {
    return localStorage.getItem(this.activeOrgKey);
  }

  getActiveOrgRole(): string | null {
    return localStorage.getItem(this.activeOrgRoleKey);
  }

  setActiveOrg(orgId: string, role?: string): Observable<{ access_token: string; token_type: string }> {
    if (role) {
      localStorage.setItem(this.activeOrgRoleKey, role);
    }
    localStorage.setItem(this.activeOrgKey, orgId);
    this.activeOrgSubject.next(orgId);
    return this.http.post<{ access_token: string; token_type: string }>(`${this.apiUrl}/orgs/${orgId}/switch`, {}).pipe(
      tap(response => {
        if (response.access_token) {
          localStorage.setItem('auth_token', response.access_token);
        }
      })
    );
  }

  clearActiveOrg(): void {
    localStorage.removeItem(this.activeOrgKey);
    localStorage.removeItem(this.activeOrgRoleKey);
    this.activeOrgSubject.next(null);
  }
}
