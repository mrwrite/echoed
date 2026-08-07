import { HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { DiagnosticService } from './diagnostic.service';

describe('DiagnosticService', () => {
  let service: DiagnosticService;

  beforeEach(() => service = new DiagnosticService());

  it('extracts only bounded safe backend request references', () => {
    const safe = new HttpErrorResponse({ status: 500, headers: new HttpHeaders({ 'X-Request-ID': 'req-ABC_123' }) });
    const unsafe = new HttpErrorResponse({ status: 500, headers: new HttpHeaders({ 'X-Request-ID': 'bad reference with spaces' }) });
    expect(service.reference(safe)).toBe('req-ABC_123');
    expect(service.reference(unsafe)).toBeUndefined();
  });

  it('records bounded metadata without response bodies, secrets, or learner content', () => {
    const warning = spyOn(console, 'warn');
    const error = new HttpErrorResponse({
      status: 500,
      headers: new HttpHeaders({ 'X-Request-ID': 'req-42' }),
      error: { password: 'never-log-this', lesson_content: 'private learner text' },
      url: '/api/login?token=secret',
    });
    service.record('Course Studio autosave', error);
    expect(warning).toHaveBeenCalledWith('EchoEd diagnostic', {
      event: 'frontend.operation.failed', operation: 'course_studio_autosave', status: 500, requestId: 'req-42',
    });
    expect(JSON.stringify(warning.calls.mostRecent().args)).not.toContain('never-log-this');
    expect(JSON.stringify(warning.calls.mostRecent().args)).not.toContain('private learner text');
  });

  it('adds support references only to unexpected server failures', () => {
    const headers = new HttpHeaders({ 'X-Request-ID': 'req-support' });
    expect(service.message('Try again.', new HttpErrorResponse({ status: 500, headers }))).toContain('Reference: req-support');
    expect(service.message('Fix the form.', new HttpErrorResponse({ status: 422, headers }))).toBe('Fix the form.');
  });
});
