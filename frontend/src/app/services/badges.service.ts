import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Badge, BadgeCreate, StudentBadge } from '../models/badge';

@Injectable({
  providedIn: 'root'
})
export class BadgesService {
  private apiUrl = `${environment.apiUrl}/api`;

  constructor(private http: HttpClient) {}

  getBadges(): Observable<Badge[]> {
    return this.http.get<Badge[]>(`${this.apiUrl}/badges`);
  }

  getStudentBadges(studentId: string): Observable<StudentBadge[]> {
    return this.http.get<StudentBadge[]>(`${this.apiUrl}/students/${studentId}/badges`);
  }

  createBadge(badge: BadgeCreate): Observable<Badge> {
    return this.http.post<Badge>(`${this.apiUrl}/badges`, badge);
  }

  uploadBadgeImage(file: File): Observable<{ file_path: string }> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<{ file_path: string }>(`${this.apiUrl}/upload/badge`, formData);
  }

  assignBadge(studentId: string, badgeId: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/students/${studentId}/badges/${badgeId}`, {});
  }
}
