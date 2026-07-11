import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { of, throwError } from 'rxjs';

import { CertificationsComponent } from './certifications.component';
import { ProgramsService } from '../../services/programs.service';
import { ToastService } from '../../services/toast.service';

class MockProgramsService {
  certificationsResponse = of([
    {
      id: 'student-cert-1',
      student_id: 'student-1',
      certification_id: 'cert-1',
      awarded_at: '2026-01-05T12:00:00Z',
      score_snapshot: 92,
      certification: {
        id: 'cert-1',
        program_id: 'program-1',
        title: 'Introduction to Africa Certificate',
        description: 'Earned through course completion and assessment.',
        created_at: '2026-01-01T00:00:00Z',
        requirements: [{ id: 'req-1', requirement_type: 'course_completion', course_id: 'course-1' }],
      },
    },
  ]);

  getMyCertifications = jasmine.createSpy('getMyCertifications').and.callFake(() => this.certificationsResponse);
}

class MockToastService {
  show = jasmine.createSpy('show');
}

describe('CertificationsComponent', () => {
  let fixture: ComponentFixture<CertificationsComponent>;
  let programsService: MockProgramsService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RouterTestingModule, CertificationsComponent],
      providers: [
        { provide: ProgramsService, useClass: MockProgramsService },
        { provide: ToastService, useClass: MockToastService },
      ],
    }).compileComponents();

    programsService = TestBed.inject(ProgramsService) as unknown as MockProgramsService;
  });

  it('renders earned certificates as student achievements without download claims', () => {
    fixture = TestBed.createComponent(CertificationsComponent);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Certificates earned through learning');
    expect(compiled.textContent).toContain('Introduction to Africa Certificate');
    expect(compiled.textContent).toContain('This certificate records completion inside EchoEd');
    expect(compiled.textContent).not.toContain('Download');
  });

  it('renders a purposeful no-certificate state', () => {
    programsService.certificationsResponse = of([]);
    fixture = TestBed.createComponent(CertificationsComponent);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('[data-echo-state="empty"]')).not.toBeNull();
    expect(compiled.textContent).toContain('Your certificates will appear here');
    expect(compiled.textContent).toContain('Browse learning paths');
  });

  it('renders a recoverable certificate load error', () => {
    programsService.certificationsResponse = throwError(() => new Error('load failed'));
    fixture = TestBed.createComponent(CertificationsComponent);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('[data-echo-state="error"]')).not.toBeNull();
    expect(compiled.textContent).toContain('We could not load your certificates');
  });
});
