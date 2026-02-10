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
  private organizationsSubject = new BehaviorSubject<Organization[]>([]);

  activeOrg$ = this.activeOrgSubject.asObservable();
  organizations$ = this.organizationsSubject.asObservable();

  constructor(private http: HttpClient) {}

  getOrganizations(): Observable<Organization[]> {
    return this.organizations$;
  }

  refreshOrganizations(): Observable<Organization[]> {
    return this.http.get<Organization[]>(`${this.apiUrl}/orgs`).pipe(
      tap(orgs => this.organizationsSubject.next(orgs))
    );
  }

  createOrganization(payload: { name: string; type: string; country?: string | null; timezone?: string | null }): Observable<Organization> {
    return this.http.post<Organization>(`${this.apiUrl}/orgs`, payload);
  }

  updateOrganization(orgId: string, payload: { name: string }): Observable<Organization> {
    return this.http.patch<Organization>(`${this.apiUrl}/orgs/${orgId}`, payload);
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
    this.organizationsSubject.next([]);
  }
}
