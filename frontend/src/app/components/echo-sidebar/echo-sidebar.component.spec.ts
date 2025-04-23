import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EchoSidebarComponent } from './echo-sidebar.component';

describe('EchoSidebarComponent', () => {
  let component: EchoSidebarComponent;
  let fixture: ComponentFixture<EchoSidebarComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EchoSidebarComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EchoSidebarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
