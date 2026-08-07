import { ErrorHandler, Injectable } from '@angular/core';
import { DiagnosticService } from './diagnostic.service';

@Injectable()
export class GlobalErrorHandler implements ErrorHandler {
  constructor(private readonly diagnostics: DiagnosticService) {}

  handleError(error: unknown): void {
    this.diagnostics.record('angular.unhandled', error);
  }
}
