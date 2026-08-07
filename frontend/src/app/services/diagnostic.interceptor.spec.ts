import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { HttpClient } from '@angular/common/http';
import { diagnosticInterceptor } from './diagnostic.interceptor';
import { DiagnosticService } from './diagnostic.service';

describe('diagnosticInterceptor', () => {
  it('records unexpected API failures and leaves the error response intact', () => {
    const diagnostics = jasmine.createSpyObj<DiagnosticService>('DiagnosticService', ['record']);
    TestBed.configureTestingModule({ providers: [
      provideHttpClient(withInterceptors([diagnosticInterceptor])),
      provideHttpClientTesting(),
      { provide: DiagnosticService, useValue: diagnostics },
    ] });
    const client = TestBed.inject(HttpClient);
    const http = TestBed.inject(HttpTestingController);
    let status = 0;
    client.get('/api/failure').subscribe({ error: error => status = error.status });
    const request = http.expectOne('/api/failure');
    request.flush({ detail: 'must not be logged by the interceptor' }, { status: 500, statusText: 'Server Error' });
    expect(status).toBe(500);
    expect(diagnostics.record).toHaveBeenCalledWith('api.request', jasmine.objectContaining({ status: 500 }));
    http.verify();
  });
});
