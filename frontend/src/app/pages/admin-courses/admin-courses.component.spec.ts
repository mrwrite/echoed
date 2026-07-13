import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { of } from 'rxjs';
import { AdminCoursesComponent } from './admin-courses.component';
import { CoursesService } from '../../services/courses.service';

describe('AdminCoursesComponent', () => {
  let fixture: ComponentFixture<AdminCoursesComponent>;
  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [RouterTestingModule, AdminCoursesComponent], providers: [
      { provide: CoursesService, useValue: { getCourses: () => of([{ id: 'course-1', title: 'World History', description: 'History course' }]), deleteCourse: () => of({}) } },
      { provide: ActivatedRoute, useValue: { snapshot: { paramMap: convertToParamMap({}) } } },
    ] }).compileComponents();
    fixture = TestBed.createComponent(AdminCoursesComponent); fixture.detectChanges();
  });

  it('renders oversight without content-authoring controls when metadata is sparse', () => {
    const text = fixture.nativeElement.textContent;
    expect(text).toContain('World History'); expect(text).toContain('Status Unavailable');
    expect(text).not.toContain('Create course'); expect(text).not.toContain('Edit course');
  });
});
