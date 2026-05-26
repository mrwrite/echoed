import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { TokenResponse } from '../models/token-response';
import { environment } from '../../environments/environment';
import { RegisterDto } from '../models/register-dto';


@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = `${environment.apiUrl}/api/auth`;
  private authTokenKey = 'auth_token';
  private activeOrgKey = 'active_org_id';
  private activeOrgRoleKey = 'active_org_role';

  constructor(private http: HttpClient) { }

  login(username: string, password: string): Observable<any> {
    const body = new URLSearchParams();
    body.set('username', username);
    body.set('password', password);

    return this.http.post<TokenResponse>(`${this.apiUrl}/token`, body.toString(), {
      headers: new HttpHeaders({ 'Content-Type': 'application/x-www-form-urlencoded' })
    }).pipe (

      tap(response => {
        this.applyTokenResponse(response);
      })
    );
  }

  register(user: RegisterDto): Observable<any> {
    return this.http.post(`${this.apiUrl}/register`, user );
  }

  logout() {
    localStorage.removeItem(this.authTokenKey);
    localStorage.removeItem(this.activeOrgKey);
    localStorage.removeItem(this.activeOrgRoleKey);
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  getToken(): string | null{
    return localStorage.getItem(this.authTokenKey);
  }

  applyTokenResponse(response: TokenResponse): void {
    this.applySessionResponse(response);
  }

  isTokenExpired(token: string): boolean {
    const payload = this.getTokenPayload(token);
    const exp = payload?.exp;

    if (typeof exp !== 'number') {
      return true;
    }

    return Date.now() >= exp * 1000;
  }

  private applySessionResponse(response: TokenResponse): void {
    localStorage.setItem(this.authTokenKey, response.access_token);

    const activeOrgId = response.active_org_id ?? null;
    if (activeOrgId) {
      localStorage.setItem(this.activeOrgKey, activeOrgId);
    } else {
      localStorage.removeItem(this.activeOrgKey);
    }

    const activeOrgRole = this.resolveActiveOrgRole(response);
    if (activeOrgRole) {
      localStorage.setItem(this.activeOrgRoleKey, activeOrgRole);
    } else {
      localStorage.removeItem(this.activeOrgRoleKey);
    }
  }

  private resolveActiveOrgRole(response: TokenResponse): string | null {
    if (response.active_org_role) {
      return response.active_org_role;
    }

    if (response.active_organization?.role) {
      return response.active_organization.role;
    }

    if (!response.active_org_id || !response.organizations?.length) {
      return null;
    }

    const matchingOrganization = response.organizations.find(
      (organization) => organization.id === response.active_org_id,
    );

    return matchingOrganization?.role ?? null;
  }

  getTokenPayload(token: string): any {
    if (!token) {
      return null;
    }
    const payloadPart = token.split('.')[1];
    if (!payloadPart) {
      return null;
    }

    try {
      const decodedPayload = atob(payloadPart.replace(/-/g, '+').replace(/_/g, '/'));
      return JSON.parse(decodedPayload);
    } catch (err) {
      console.error('Error parsing token payload:', err);
      return null;
    }
  }

  isSuperAdminRole(role?: string | null): boolean {
    if (!role) {
      return false;
    }

    const normalized = role.toLowerCase();
    return normalized === 'super_admin' || normalized === 'superadmin';
  }
}
