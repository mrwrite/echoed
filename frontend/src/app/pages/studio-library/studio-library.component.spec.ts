import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { of, throwError } from 'rxjs';
import { StudioLibraryComponent } from './studio-library.component';
import { V2PlatformService } from '../../services/v2-platform.service';

describe('StudioLibraryComponent', () => {
  let fixture: ComponentFixture<StudioLibraryComponent>;
  const platform = jasmine.createSpyObj('V2PlatformService', ['getProducts', 'getProjects', 'getKnowledgeSources', 'getArtifacts']);
  const products = [
    { id: 'course-1', title: 'Africa and the World', product_type: 'course', course_id: 'runtime-1', description: 'Course description', status: 'draft', review_state: 'in_review', visibility: 'private' },
    { id: 'path-1', title: 'History Path', product_type: 'learning_path', program_id: null, description: null, subtitle: null, status: 'published', review_state: 'approved', visibility: 'public' },
  ] as any;

  beforeEach(async () => {
    platform.getProducts.calls.reset();
    platform.getProjects.calls.reset();
    platform.getKnowledgeSources.calls.reset();
    platform.getArtifacts.calls.reset();
    platform.getProducts.and.returnValue(of(products)); platform.getProjects.and.returnValue(of([])); platform.getKnowledgeSources.and.returnValue(of([])); platform.getArtifacts.and.returnValue(of([]));
    await TestBed.configureTestingModule({ imports: [RouterTestingModule, StudioLibraryComponent], providers: [
      { provide: V2PlatformService, useValue: platform }, { provide: ActivatedRoute, useValue: { data: of({ mode: 'courses' }) } },
    ] }).compileComponents();
    fixture = TestBed.createComponent(StudioLibraryComponent); fixture.detectChanges();
  });

  it('filters course wrappers without exposing unrelated paths', () => {
    expect(fixture.nativeElement.textContent).toContain('Africa and the World');
    expect(fixture.nativeElement.textContent).not.toContain('History Path');
    expect(fixture.nativeElement.textContent).toContain('1 item shown');
  });

  it('supports accessible search and status filters', () => {
    fixture.componentInstance.search = 'missing'; fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('0 items shown');
    expect(fixture.nativeElement.textContent).toContain('No items match these filters');
  });

  it('shows a retryable load failure', () => {
    platform.getProducts.and.returnValue(throwError(() => new Error('failed')));
    fixture.componentInstance.load(); fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Course wrappers could not be loaded');
  });
});
