import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { of, throwError } from 'rxjs';
import { StudioOverviewComponent } from './studio-overview.component';
import { AnalyticsService } from '../../services/analytics.service';
import { V2PlatformService } from '../../services/v2-platform.service';

describe('StudioOverviewComponent', () => {
  let fixture: ComponentFixture<StudioOverviewComponent>;
  const analytics = jasmine.createSpyObj('AnalyticsService', ['getV2WorkspaceAnalytics']);
  const platform = jasmine.createSpyObj('V2PlatformService', ['getReviewCenter']);
  const summary = { totals: { total_projects: 2, total_products: 3, total_knowledge_sources: 4, total_artifacts: 5 }, review_health: { published_products: 1 } } as any;
  const review = { pending_artifacts: [{ id: 'draft-1' }], draft_products: [], lesson_governance_items: [], recent_activity: [] } as any;

  beforeEach(async () => {
    analytics.getV2WorkspaceAnalytics.calls.reset(); platform.getReviewCenter.calls.reset();
    analytics.getV2WorkspaceAnalytics.and.returnValue(of(summary)); platform.getReviewCenter.and.returnValue(of(review));
    await TestBed.configureTestingModule({ imports: [RouterTestingModule, StudioOverviewComponent], providers: [
      { provide: AnalyticsService, useValue: analytics }, { provide: V2PlatformService, useValue: platform },
    ] }).compileComponents();
  });

  it('shows supported content counts and review attention', () => {
    fixture = TestBed.createComponent(StudioOverviewComponent); fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Content drafts');
    expect(fixture.nativeElement.textContent).toContain('Source records');
    expect(fixture.nativeElement.textContent).toContain('Current authoring scope');
  });

  it('keeps review work visible after a partial summary failure', () => {
    analytics.getV2WorkspaceAnalytics.and.returnValue(throwError(() => new Error('failed')));
    fixture = TestBed.createComponent(StudioOverviewComponent); fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Some Studio information could not be loaded');
    expect(fixture.nativeElement.textContent).toContain('Content drafts');
  });

  it('shows an honest empty attention state', () => {
    platform.getReviewCenter.and.returnValue(of({ pending_artifacts: [], draft_products: [], lesson_governance_items: [], recent_activity: [] }));
    fixture = TestBed.createComponent(StudioOverviewComponent); fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('No supported review items currently require attention');
  });
});
