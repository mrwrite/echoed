import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CourseWizardComponent } from './course-wizard.component';

describe('CourseWizardComponent', () => {
  let component: CourseWizardComponent;
  let fixture: ComponentFixture<CourseWizardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CourseWizardComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CourseWizardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
