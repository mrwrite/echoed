import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Assignment, Enrollment, Section, SectionSummary } from '../models/section';

@Injectable({
  providedIn: 'root'
})
export class SectionsService {
  private apiUrl = `${environment.apiUrl}/api`;

  constructor(private http: HttpClient) {}

  listSections(): Observable<Section[]> {
    return this.http.get<Section[]>(`${this.apiUrl}/sections`);
  }

  createSection(payload: Partial<Section>): Observable<Section> {
    return this.http.post<Section>(`${this.apiUrl}/sections`, payload);
  }

  getRoster(sectionId: string): Observable<Enrollment[]> {
    return this.http.get<Enrollment[]>(`${this.apiUrl}/sections/${sectionId}/roster`);
  }

  getSectionSummary(sectionId: string): Observable<SectionSummary> {
    return this.http.get<SectionSummary>(`${this.apiUrl}/sections/${sectionId}/analytics/summary`);
  }

  getAssignments(sectionId: string): Observable<Assignment[]> {
    return this.http.get<Assignment[]>(`${this.apiUrl}/sections/${sectionId}/assignments`);
  }

  createAssignment(sectionId: string, payload: Partial<Assignment>): Observable<Assignment> {
    return this.http.post<Assignment>(`${this.apiUrl}/sections/${sectionId}/assignments`, payload);
  }
}
