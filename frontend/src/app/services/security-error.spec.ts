import { HttpErrorResponse, HttpHeaders } from '@angular/common/http';

import { securityErrorMessage } from './security-error';

describe('securityErrorMessage', () => {
  it('maps authentication, permission, concealed, and rate-limit responses safely', () => {
    expect(securityErrorMessage(new HttpErrorResponse({ status: 401 }), 'fallback')).toContain('Sign in');
    expect(securityErrorMessage(new HttpErrorResponse({ status: 403 }), 'fallback')).toContain('permission');
    expect(securityErrorMessage(new HttpErrorResponse({ status: 404 }), 'fallback')).toContain('unavailable');
    expect(securityErrorMessage(new HttpErrorResponse({ status: 429, headers: new HttpHeaders({ 'Retry-After': '30' }) }), 'fallback')).toContain('Too many');
  });

  it('preserves an actionable administrator conflict without exposing unknown errors', () => {
    expect(securityErrorMessage(new HttpErrorResponse({ status: 409, error: { detail: 'This action would remove the final platform super administrator.' } }), 'fallback')).toContain('final platform');
    expect(securityErrorMessage(new Error('internal database details'), 'Safe fallback')).toBe('Safe fallback');
  });

  it('adds a safe request reference to unexpected server errors', () => {
    const error = new HttpErrorResponse({ status: 500, headers: new HttpHeaders({ 'X-Request-ID': 'req-500' }) });
    expect(securityErrorMessage(error, 'Something went wrong.')).toBe('Something went wrong. Reference: req-500');
  });
});
