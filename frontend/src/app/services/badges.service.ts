import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthService } from './auth.service';
import { Badge, BadgeCreate } from '../models/badge';

@Injectable({
  providedIn: 'root'
})
export class BadgesService {
  private apiUrl = `${environment.apiUrl}/api`;

  constructor(private http: HttpClient, private authService: AuthService) {}

  private getHeaders(): HttpHeaders {
    let token = this.authService.getToken();
    if (token && !token.startsWith('Bearer ')) {
      token = `Bearer ${token}`;
    } else if (!token) {
      token = `Bearer ${this.authService.getToken()}`;
    }
    return new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: token || ''
    });
  }

  private getFileHeaders(): HttpHeaders {
    let token = this.authService.getToken();
    if (token && !token.startsWith('Bearer ')) {
      token = `Bearer ${token}`;
    } else if (!token) {
      token = `Bearer ${this.authService.getToken()}`;
    }
    return new HttpHeaders({ Authorization: token || '' });
  }

  getBadges(): Observable<Badge[]> {
    return this.http.get<Badge[]>(`${this.apiUrl}/badges`, { headers: this.getHeaders() });
  }

  createBadge(badge: BadgeCreate): Observable<Badge> {
    return this.http.post<Badge>(`${this.apiUrl}/badges`, badge, { headers: this.getHeaders() });
  }

  uploadBadgeImage(file: File): Observable<{ file_path: string }> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<{ file_path: string }>(`${this.apiUrl}/upload/badge`, formData, { headers: this.getFileHeaders() });
  }

  assignBadge(studentId: string, badgeId: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/students/${studentId}/badges/${badgeId}`, {}, {
      headers: this.getHeaders()
    });
  }
}
