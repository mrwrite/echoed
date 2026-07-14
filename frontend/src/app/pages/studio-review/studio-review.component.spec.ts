import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { of, throwError } from 'rxjs';
import { StudioReviewComponent } from './studio-review.component';
import { V2PlatformService } from '../../services/v2-platform.service';

describe('StudioReviewComponent', () => {
  let fixture: ComponentFixture<StudioReviewComponent>;
  const platform = jasmine.createSpyObj('V2PlatformService', ['getReviewCenter', 'updateArtifactReviewStatus', 'updateProductReviewStatus']);
  const item = { id: 'draft-1', item_type: 'artifact', title: 'Lesson outline', status: 'in_review', review_state: 'in_review', source_coverage: 'Source linked', readiness: 'Wrapper review only', required_decision: 'Review', blocked: false } as any;

  beforeEach(async () => {
    platform.getReviewCenter.calls.reset(); platform.updateArtifactReviewStatus.calls.reset(); platform.updateProductReviewStatus.calls.reset();
    platform.getReviewCenter.and.returnValue(of({ pending_artifacts: [item], draft_products: [], lesson_governance_items: [], recent_activity: [] }));
    platform.updateArtifactReviewStatus.and.returnValue(of({ ...item, status: 'approved' }));
    await TestBed.configureTestingModule({ imports: [RouterTestingModule, StudioReviewComponent], providers: [{ provide: V2PlatformService, useValue: platform }] }).compileComponents();
    fixture = TestBed.createComponent(StudioReviewComponent); fixture.detectChanges();
  });

  it('requires confirmation before recording a review decision', () => {
    fixture.componentInstance.requestDecision(item, 'approved');
    expect(platform.updateArtifactReviewStatus).not.toHaveBeenCalled();
    fixture.componentInstance.applyDecision();
    expect(platform.updateArtifactReviewStatus).toHaveBeenCalledWith('draft-1', { status: 'approved' });
  });

  it('preserves the pending decision after a failed mutation', () => {
    platform.updateArtifactReviewStatus.and.returnValue(throwError(() => new Error('failed')));
    fixture.componentInstance.requestDecision(item, 'rejected'); fixture.componentInstance.applyDecision();
    expect(fixture.componentInstance.decision?.status).toBe('rejected');
    expect(fixture.componentInstance.actionError).toContain('not changed');
  });
});
