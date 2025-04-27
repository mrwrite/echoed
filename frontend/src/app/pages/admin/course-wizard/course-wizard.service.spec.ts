import { TestBed } from '@angular/core/testing';

import { CourseWizardService } from './course-wizard.service';

describe('CourseWizardService', () => {
  let service: CourseWizardService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CourseWizardService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
