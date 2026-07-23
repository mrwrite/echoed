import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap, provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { V2PlatformService } from '../../services/v2-platform.service';
import { PublicProductDetailComponent } from './public-product-detail.component';

describe('PublicProductDetailComponent', () => {
  it('renders one product heading and a real access path', async () => {
    const service = jasmine.createSpyObj<V2PlatformService>('V2PlatformService', ['getPublicProduct']);
    service.getPublicProduct.and.returnValue(of({ id: '1', slug: 'history', title: 'History in Community', product_type: 'course' } as any));
    await TestBed.configureTestingModule({
      imports: [PublicProductDetailComponent],
      providers: [provideRouter([]), { provide: V2PlatformService, useValue: service }, { provide: ActivatedRoute, useValue: { snapshot: { paramMap: convertToParamMap({ slug: 'history' }) } } }],
    }).compileComponents();
    const fixture = TestBed.createComponent(PublicProductDetailComponent);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelectorAll('h1').length).toBe(1);
    expect(fixture.nativeElement.querySelector('.access-link').textContent).toContain('Sign in');
    expect(fixture.nativeElement.querySelector('button[disabled]')).toBeNull();
  });
});
