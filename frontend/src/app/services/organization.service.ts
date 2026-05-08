import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Organization } from '../models/organization';
import { AuthService } from './auth.service';
import { TokenResponse } from '../models/token-response';

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

  get organizationsSubjectValue(): Organization[] {
    return this.organizationsSubject.value;
  }

  constructor(
    private http: HttpClient,
    private authService: AuthService,
  ) {}

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

  setActiveOrg(orgId: string, role?: string): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${this.apiUrl}/orgs/${orgId}/switch`, {}).pipe(
      tap(response => {
        this.authService.applyTokenResponse(response);
        this.activeOrgSubject.next(response.active_org_id ?? null);
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
