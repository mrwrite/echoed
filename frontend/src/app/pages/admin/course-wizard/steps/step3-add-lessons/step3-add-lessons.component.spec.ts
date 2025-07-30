import { RouterTestingModule } from '@angular/router/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Step3AddLessonsComponent } from './step3-add-lessons.component';

describe('Step3AddLessonsComponent', () => {
  let component: Step3AddLessonsComponent;
  let fixture: ComponentFixture<Step3AddLessonsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RouterTestingModule, HttpClientTestingModule, Step3AddLessonsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Step3AddLessonsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
