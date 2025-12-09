import { RouterTestingModule } from '@angular/router/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Step2AddUnitsComponent } from './step2-add-units.component';

describe('Step2AddUnitsComponent', () => {
  let component: Step2AddUnitsComponent;
  let fixture: ComponentFixture<Step2AddUnitsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RouterTestingModule, HttpClientTestingModule, Step2AddUnitsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Step2AddUnitsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
