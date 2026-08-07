import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { DiagnosticService } from './diagnostic.service';

export const diagnosticInterceptor: HttpInterceptorFn = (request, next) => {
  const diagnostics = inject(DiagnosticService);
  return next(request).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 0 || error.status >= 500) diagnostics.record('api.request', error);
      return throwError(() => error);
    }),
  );
};
