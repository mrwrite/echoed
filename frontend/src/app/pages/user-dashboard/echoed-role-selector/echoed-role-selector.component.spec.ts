import { RouterTestingModule } from '@angular/router/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EchoedRoleSelectorComponent } from './echoed-role-selector.component';

describe('EchoedRoleSelectorComponent', () => {
  let component: EchoedRoleSelectorComponent;
  let fixture: ComponentFixture<EchoedRoleSelectorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RouterTestingModule, HttpClientTestingModule, EchoedRoleSelectorComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EchoedRoleSelectorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
