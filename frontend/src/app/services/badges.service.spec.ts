import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { environment } from '../../environments/environment';
import { BadgesService } from './badges.service';

describe('BadgesService', () => {
  let service: BadgesService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule]
    });
    service = TestBed.inject(BadgesService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('does not manually attach Authorization on badge image uploads', () => {
    const file = new File(['badge'], 'badge.png', { type: 'image/png' });

    service.uploadBadgeImage(file).subscribe();

    const req = httpMock.expectOne(`${environment.apiUrl}/api/upload/badge`);
    expect(req.request.headers.has('Authorization')).toBeFalse();
    expect(req.request.body instanceof FormData).toBeTrue();
    req.flush({ file_path: '/uploads/badge.png' });
  });
});
