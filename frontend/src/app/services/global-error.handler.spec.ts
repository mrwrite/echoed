import { GlobalErrorHandler } from './global-error.handler';
import { DiagnosticService } from './diagnostic.service';

describe('GlobalErrorHandler', () => {
  it('routes unhandled failures through the safe diagnostic service', () => {
    const diagnostics = jasmine.createSpyObj<DiagnosticService>('DiagnosticService', ['record']);
    const handler = new GlobalErrorHandler(diagnostics);
    const failure = new Error('private stack detail');
    handler.handleError(failure);
    expect(diagnostics.record).toHaveBeenCalledWith('angular.unhandled', failure);
  });
});
