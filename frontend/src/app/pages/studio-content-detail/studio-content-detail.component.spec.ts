import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { of, throwError } from 'rxjs';
import { StudioContentDetailComponent } from './studio-content-detail.component';
import { V2PlatformService } from '../../services/v2-platform.service';

describe('StudioContentDetailComponent', () => {
  let fixture: ComponentFixture<StudioContentDetailComponent>;
  const platform = jasmine.createSpyObj('V2PlatformService', ['getProduct', 'publishProduct']);
  const product = { id: 'product-1', title: 'History Course', product_type: 'course', description: 'Description', status: 'approved', review_state: 'approved', visibility: 'private', access_state: 'private', course_id: 'course-1', program_id: null, updated_at: '2026-07-13T00:00:00Z' } as any;

  beforeEach(async () => {
    platform.getProduct.calls.reset(); platform.publishProduct.calls.reset();
    platform.getProduct.and.returnValue(of(product)); platform.publishProduct.and.returnValue(of({ ...product, status: 'published', visibility: 'public', slug: 'history-course' }));
    await TestBed.configureTestingModule({ imports: [RouterTestingModule, StudioContentDetailComponent], providers: [
      { provide: V2PlatformService, useValue: platform }, { provide: ActivatedRoute, useValue: { snapshot: { paramMap: convertToParamMap({ productId: 'product-1' }) } } },
    ] }).compileComponents();
    fixture = TestBed.createComponent(StudioContentDetailComponent); fixture.detectChanges();
  });

  it('requires confirmation before public publishing', () => {
    fixture.componentInstance.requestPublish();
    expect(fixture.componentInstance.confirmPublish).toBeTrue();
    expect(platform.publishProduct).not.toHaveBeenCalled();
    fixture.componentInstance.publish();
    expect(platform.publishProduct).toHaveBeenCalledWith('product-1', { visibility: 'public' });
    expect(fixture.componentInstance.product?.status).toBe('published');
  });

  it('does not optimistically publish after an API failure', () => {
    platform.publishProduct.and.returnValue(throwError(() => new Error('failed')));
    fixture.componentInstance.requestPublish(); fixture.componentInstance.publish();
    expect(fixture.componentInstance.product?.status).toBe('approved');
    expect(fixture.componentInstance.actionError).toContain('has not changed');
  });
});
