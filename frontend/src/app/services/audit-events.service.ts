import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import { AuditEventFilters, AuditEventPage } from '../models/audit-event';

@Injectable({ providedIn: 'root' })
export class AuditEventsService {
  private readonly apiUrl = `${environment.apiUrl}/api/audit-events`;

  constructor(private readonly http: HttpClient) {}

  list(filters: AuditEventFilters = {}): Observable<AuditEventPage> {
    let params = new HttpParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== '') params = params.set(key, String(value));
    });
    return this.http.get<AuditEventPage>(this.apiUrl, { params });
  }

  export(filters: Pick<AuditEventFilters, 'action' | 'category' | 'outcome'> = {}): Observable<Blob> {
    let params = new HttpParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params = params.set(key, value);
    });
    return this.http.get(`${this.apiUrl}/export.csv`, { params, responseType: 'blob' });
  }
}
