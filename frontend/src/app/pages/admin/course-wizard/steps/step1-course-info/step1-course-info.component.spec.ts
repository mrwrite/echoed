import { RouterTestingModule } from '@angular/router/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Step1CourseInfoComponent } from './step1-course-info.component';

describe('Step1CourseInfoComponent', () => {
  let component: Step1CourseInfoComponent;
  let fixture: ComponentFixture<Step1CourseInfoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RouterTestingModule, HttpClientTestingModule, Step1CourseInfoComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Step1CourseInfoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
