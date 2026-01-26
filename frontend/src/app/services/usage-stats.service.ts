import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { AnalyticsService } from './analytics.service';

export interface UsageStat {
  label: string;
  value: number;
  color: string;
  description?: string;
}

@Injectable({ providedIn: 'root' })
export class UsageStatsService {
  constructor(private analyticsService: AnalyticsService) {}

  getUsageStats(): Observable<UsageStat[]> {
    return this.analyticsService.getAdminOverview().pipe(
      map(overview => {
        const progress = overview.progress;
        const totals = overview.totals;
        const activeStudentsPercent = totals.students
          ? Math.round((totals.active_students / totals.students) * 100)
          : 0;
        return [
          { label: 'Course Completion Rate', value: progress.course_completion_rate, color: 'bg-primary' },
          { label: 'Lessons Completed', value: Math.min(progress.lessons_completed, 100), color: 'bg-secondary' },
          { label: 'Active Students', value: activeStudentsPercent, color: 'bg-accent' },
        ];
      })
    );
  }
}
