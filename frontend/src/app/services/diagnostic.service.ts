import { HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { requestReference, withSupportReference } from './security-error';

export interface SafeFrontendDiagnostic {
  event: string;
  operation: string;
  status?: number;
  requestId?: string;
}

@Injectable({ providedIn: 'root' })
export class DiagnosticService {
  private readonly reported = new WeakSet<object>();

  reference(error: unknown): string | undefined {
    return requestReference(error);
  }

  message(message: string, error: unknown): string {
    return withSupportReference(message, error);
  }

  record(operation: string, error: unknown): void {
    if (error && typeof error === 'object') {
      if (this.reported.has(error)) return;
      this.reported.add(error);
    }

    const response = error as HttpErrorResponse | undefined;
    const diagnostic: SafeFrontendDiagnostic = {
      event: 'frontend.operation.failed',
      operation: this.safeOperation(operation),
    };
    if (typeof response?.status === 'number') diagnostic.status = response.status;
    const requestId = this.reference(error);
    if (requestId) diagnostic.requestId = requestId;

    // Deliberately exclude the exception, response body, URL, headers, and form state.
    console.warn('EchoEd diagnostic', diagnostic);
  }

  private safeOperation(operation: string): string {
    const normalized = operation.toLowerCase().replace(/[^a-z0-9._-]/g, '_').slice(0, 64);
    return normalized || 'unknown';
  }
}
