import { RouterTestingModule } from '@angular/router/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TeacherViewComponent } from './teacher-view.component';

describe('TeacherViewComponent', () => {
  let component: TeacherViewComponent;
  let fixture: ComponentFixture<TeacherViewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RouterTestingModule, HttpClientTestingModule, TeacherViewComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(TeacherViewComponent);
    component = fixture.componentInstance;
    component.userInfo = { fullname: 'Test User', role: 'teacher' } as any;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
