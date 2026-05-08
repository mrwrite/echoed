import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LessonViewerComponent } from './lesson-viewer.component';

describe('LessonViewerComponent', () => {
  let component: LessonViewerComponent;
  let fixture: ComponentFixture<LessonViewerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LessonViewerComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(LessonViewerComponent);
    component = fixture.componentInstance;
    component.lesson = {
      id: 'lesson-1',
      title: 'Evidence and Claims',
      teacher_notes: 'Prompt students to compare the two sources.',
      discussion_questions: ['Which source is more credible?'],
      activities: [],
    };
  });

  it('hides educator-only notes in learner mode while preserving learner prompts', () => {
    component.isTeacherLed = false;
    fixture.detectChanges();

    const text = fixture.nativeElement.textContent;
    expect(text).not.toContain('Teacher Notes');
    expect(text).toContain('Which source is more credible?');
  });

  it('shows educator-only fields in teacher-led mode', () => {
    component.isTeacherLed = true;
    fixture.detectChanges();

    const text = fixture.nativeElement.textContent;
    expect(text).toContain('Teacher Notes');
    expect(text).toContain('Which source is more credible?');
  });
});
