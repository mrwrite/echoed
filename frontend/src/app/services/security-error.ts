import { HttpErrorResponse } from '@angular/common/http';

const SAFE_REFERENCE = /^[A-Za-z0-9._:-]{1,128}$/;

export function requestReference(error: unknown): string | undefined {
  const response = error as HttpErrorResponse | undefined;
  const candidate = response?.headers?.get('X-Request-ID') ??
    (typeof response?.error?.request_id === 'string' ? response.error.request_id : undefined);
  return candidate && SAFE_REFERENCE.test(candidate) ? candidate : undefined;
}

export function withSupportReference(message: string, error: unknown): string {
  const response = error as HttpErrorResponse | undefined;
  const reference = response?.status && response.status >= 500 ? requestReference(error) : undefined;
  return reference ? `${message} Reference: ${reference}` : message;
}

export function securityErrorMessage(error: unknown, fallback: string): string {
  const response = error as HttpErrorResponse | undefined;
  switch (response?.status) {
    case 401:
      return 'Your session has expired or is invalid. Sign in and try again.';
    case 403:
      return 'Your account does not have permission for this action.';
    case 404:
      return 'This record is unavailable or you do not have access to it.';
    case 409:
    case 422:
      return typeof response.error?.detail === 'string' ? response.error.detail : fallback;
    case 429:
      return 'Too many attempts. Wait a moment, then try again.';
    default:
      return withSupportReference(fallback, error);
  }
}
