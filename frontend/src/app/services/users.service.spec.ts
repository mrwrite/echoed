import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { UsersService } from './users.service';
import { environment } from '../../environments/environment';

describe('UsersService', () => {
  let service: UsersService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule]
    });
    service = TestBed.inject(UsersService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('sends only the allowlisted role field for a privileged role change', () => {
    const user = { id: 'user-1', firstname: 'Ada', lastname: 'Lovelace', username: 'ada', email: 'ada@example.test', role: 'student', created_at: new Date() };
    service.updateUserRole(user, 'teacher').subscribe();
    const request = httpMock.expectOne(`${environment.apiUrl}/api/users/user-1`);
    expect(request.request.body).toEqual({ role: 'teacher' });
    expect(request.request.body.password).toBeUndefined();
    request.flush({ message: 'ok' });
  });
});
