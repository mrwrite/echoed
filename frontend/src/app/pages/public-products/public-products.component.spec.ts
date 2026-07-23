import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of, throwError } from 'rxjs';
import { V2PlatformService } from '../../services/v2-platform.service';
import { PublicProductsComponent } from './public-products.component';

describe('PublicProductsComponent', () => {
  it('renders reviewed products with descriptive links', async () => {
    const service = jasmine.createSpyObj<V2PlatformService>('V2PlatformService', ['getPublicProducts']);
    service.getPublicProducts.and.returnValue(of([{ id: '1', slug: 'history', title: 'History in Community', product_type: 'course' } as any]));
    await TestBed.configureTestingModule({ imports: [PublicProductsComponent], providers: [provideRouter([]), { provide: V2PlatformService, useValue: service }] }).compileComponents();
    const fixture = TestBed.createComponent(PublicProductsComponent);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('h2').textContent).toContain('History in Community');
    expect(fixture.nativeElement.querySelector('a').textContent).toContain('View product');
  });

  it('shows an announced retryable error instead of an empty catalog', async () => {
    const service = jasmine.createSpyObj<V2PlatformService>('V2PlatformService', ['getPublicProducts']);
    service.getPublicProducts.and.returnValue(throwError(() => new Error('offline')));
    await TestBed.configureTestingModule({ imports: [PublicProductsComponent], providers: [provideRouter([]), { provide: V2PlatformService, useValue: service }] }).compileComponents();
    const fixture = TestBed.createComponent(PublicProductsComponent);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('[data-echo-state="error"]')).not.toBeNull();
    expect(fixture.nativeElement.textContent).toContain('No product information changed.');
  });
});
