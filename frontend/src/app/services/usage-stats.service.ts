import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';

export interface UsageStat {
  label: string;
  value: number;
  color: string;
  description?: string;
}

@Injectable({ providedIn: 'root' })
export class UsageStatsService {
  getUsageStats(): Observable<UsageStat[]> {
    // Demo-friendly data; can be replaced with real API aggregation later
    const stats: UsageStat[] = [
      { label: 'Lessons Completed', value: 82, color: 'bg-primary' },
      { label: 'Assignments Submitted', value: 68, color: 'bg-secondary' },
      { label: 'Active Students', value: 74, color: 'bg-accent' },
    ];
    return of(stats);
  }
}
