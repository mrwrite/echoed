import { TestBed } from '@angular/core/testing';
import { NavigationError, Router } from '@angular/router';
import { DiagnosticService } from '../services/diagnostic.service';
import { isLazyChunkLoadError, recoverFromNavigationError } from './navigation-error.handler';

describe('navigation error recovery', () => {
  it('recognizes browser dynamic-import failures', () => {
    const error = new NavigationError(
      1,
      '/studio',
      new TypeError('Failed to fetch dynamically imported module'),
    );

    expect(isLazyChunkLoadError(error)).toBeTrue();
  });

  it('recognizes webpack-compatible chunk failures', () => {
    const error = new NavigationError(2, '/learn', new Error('Loading chunk 42 failed'));

    expect(isLazyChunkLoadError(error)).toBeTrue();
  });

  it('does not redirect unrelated navigation errors', () => {
    const error = new NavigationError(3, '/admin', new Error('Resolver rejected the request'));

    expect(isLazyChunkLoadError(error)).toBeFalse();
  });

  it('records a bounded lazy-chunk category before redirecting to recovery', () => {
    const diagnostics = jasmine.createSpyObj<DiagnosticService>('DiagnosticService', ['record']);
    const router = jasmine.createSpyObj<Router>('Router', ['parseUrl']);
    router.parseUrl.and.returnValue({} as never);
    TestBed.configureTestingModule({ providers: [
      { provide: DiagnosticService, useValue: diagnostics },
      { provide: Router, useValue: router },
    ] });
    const cause = new Error('Loading chunk 42 failed');
    const error = new NavigationError(4, '/studio', cause);
    const result = TestBed.runInInjectionContext(() => recoverFromNavigationError(error));
    expect(result).toBeDefined();
    expect(diagnostics.record).toHaveBeenCalledWith('navigation.lazy_chunk', cause);
  });
});
