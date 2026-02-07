import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { OrganizationInvite } from '../models/organization';

@Injectable({
  providedIn: 'root'
})
export class InvitesService {
  private apiUrl = `${environment.apiUrl}/api`;

  constructor(private http: HttpClient) {}

  listInvites(orgId: string): Observable<OrganizationInvite[]> {
    return this.http.get<OrganizationInvite[]>(`${this.apiUrl}/orgs/${orgId}/invites`);
  }

  createInvite(orgId: string, payload: { email: string; role: string }): Observable<OrganizationInvite> {
    return this.http.post<OrganizationInvite>(`${this.apiUrl}/orgs/${orgId}/invites`, payload);
  }
}
