import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Step4ReviewSaveComponent } from './step4-review-save.component';

describe('Step4ReviewSaveComponent', () => {
  let component: Step4ReviewSaveComponent;
  let fixture: ComponentFixture<Step4ReviewSaveComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Step4ReviewSaveComponent]
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
