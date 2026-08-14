import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { environment } from '../../environments/environment';
import { AuditEventsService } from './audit-events.service';

describe('AuditEventsService', () => {
  let service: AuditEventsService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting()] });
    service = TestBed.inject(AuditEventsService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('sends only bounded review filters', () => {
    service.list({ action: 'platform.role.changed', outcome: 'succeeded', limit: 50 }).subscribe();
    const request = http.expectOne(req => req.url === `${environment.apiUrl}/api/audit-events`);
    expect(request.request.params.get('action')).toBe('platform.role.changed');
    expect(request.request.params.get('outcome')).toBe('succeeded');
    expect(request.request.params.get('limit')).toBe('50');
    request.flush({ items: [], next_cursor: null });
  });

  it('requests a blob export without adding response fields', () => {
    service.export({ category: 'access' }).subscribe();
    const request = http.expectOne(req => req.url.endsWith('/api/audit-events/export.csv'));
    expect(request.request.responseType).toBe('blob');
    expect(request.request.params.get('category')).toBe('access');
    request.flush(new Blob(['event_id\n']));
  });
});
