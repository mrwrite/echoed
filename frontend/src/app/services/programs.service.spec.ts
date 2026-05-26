import { HttpClientTestingModule } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { ProgramsService } from './programs.service';

describe('ProgramsService', () => {
  let service: ProgramsService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule]
    });
    service = TestBed.inject(ProgramsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
