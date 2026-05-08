import { HttpClient } from '@angular/common/http';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { OrganizationService } from './organization.service';
import { orgInterceptor } from './org.interceptor';

describe('orgInterceptor', () => {
  let http: HttpClient;
  let httpMock: HttpTestingController;
  let organizationService: jasmine.SpyObj<OrganizationService>;

  beforeEach(() => {
    organizationService = jasmine.createSpyObj<OrganizationService>('OrganizationService', ['getActiveOrgId']);

    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([orgInterceptor])),
        provideHttpClientTesting(),
        { provide: OrganizationService, useValue: organizationService }
      ]
    });

    http = TestBed.inject(HttpClient);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('attaches X-Org-Id from confirmed active org state', () => {
    organizationService.getActiveOrgId.and.returnValue('org-123');

    http.get('/api/test').subscribe();

    const req = httpMock.expectOne('/api/test');
    expect(req.request.headers.get('X-Org-Id')).toBe('org-123');
    req.flush({});
  });

  it('leaves requests untouched when no active org is present', () => {
    organizationService.getActiveOrgId.and.returnValue(null);

    http.get('/api/test').subscribe();

    const req = httpMock.expectOne('/api/test');
    expect(req.request.headers.has('X-Org-Id')).toBeFalse();
    req.flush({});
  });
});
