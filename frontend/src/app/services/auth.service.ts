import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
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
        localStorage.setItem(this.authTokenKey, response.access_token);
        if (response.active_org_id) {
          localStorage.setItem(this.activeOrgKey, response.active_org_id);
        }
        if (response.organizations && response.organizations.length > 0) {
          localStorage.setItem(this.activeOrgRoleKey, response.organizations[0].role);
        }
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
