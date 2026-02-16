import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, shareReplay } from 'rxjs';

export interface EnumOption {
  key: string;
  value: string;
  label: string;
}

export interface EnumsResponse {
  organizationRoles: EnumOption[];
  organizationTypes: EnumOption[];
}

@Injectable({ providedIn: 'root' })
export class MetaService {
  private enums$?: Observable<EnumsResponse>;

  constructor(private http: HttpClient) {}

  getEnums(): Observable<EnumsResponse> {
    if (!this.enums$) {
      this.enums$ = this.http
        .get<EnumsResponse>('/api/meta/enums')
        .pipe(shareReplay(1));
    }
    return this.enums$;
  }
}