import { RouterTestingModule } from '@angular/router/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Step4ReviewSaveComponent } from './step4-review-save.component';

describe('Step4ReviewSaveComponent', () => {
  let component: Step4ReviewSaveComponent;
  let fixture: ComponentFixture<Step4ReviewSaveComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RouterTestingModule, HttpClientTestingModule, Step4ReviewSaveComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Step4ReviewSaveComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
