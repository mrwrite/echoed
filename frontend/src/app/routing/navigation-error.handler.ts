import { inject } from '@angular/core';
import { NavigationError, RedirectCommand, Router } from '@angular/router';

const LAZY_CHUNK_ERROR_PATTERNS = [
  /ChunkLoadError/i,
  /Loading chunk [\w-]+ failed/i,
  /Failed to fetch dynamically imported module/i,
  /Importing a module script failed/i,
];

function errorText(error: NavigationError): string {
  const cause = error.error;
  if (cause instanceof Error) {
    return `${cause.name}: ${cause.message}`;
  }

  return String(cause ?? '');
}

export function isLazyChunkLoadError(error: NavigationError): boolean {
  const text = errorText(error);
  return LAZY_CHUNK_ERROR_PATTERNS.some((pattern) => pattern.test(text));
}

export function recoverFromNavigationError(error: NavigationError): RedirectCommand | void {
  if (!isLazyChunkLoadError(error) || error.url.startsWith('/load-error')) {
    return;
  }

  const router = inject(Router);
  return new RedirectCommand(router.parseUrl('/load-error'), {
    replaceUrl: true,
    state: { retryUrl: error.url },
  });
}
