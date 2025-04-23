import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EchoHeaderComponent } from './echo-header.component';

describe('EchoHeaderComponent', () => {
  let component: EchoHeaderComponent;
  let fixture: ComponentFixture<EchoHeaderComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EchoHeaderComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EchoHeaderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
