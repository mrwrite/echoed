import { NavigationError } from '@angular/router';
import { isLazyChunkLoadError } from './navigation-error.handler';

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
});
