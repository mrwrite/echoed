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
      hook: 'Open with a claim.',
      content: 'Read the source text carefully.',
      guided_practice: 'Model a supporting example.',
      teacher_notes: 'Prompt students to compare the two sources.',
      discussion_questions: ['Which source is more credible?'],
      activities: [{ title: 'Wrap Up', type: 'checkpoint', content: 'Summarize your evidence.' } as any],
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

  it('keeps instructional section hierarchy visible for learner content', () => {
    component.isTeacherLed = false;
    fixture.detectChanges();

    const sections = fixture.nativeElement.querySelectorAll('[aria-label="Instructional sections"] section');
    expect(sections.length).toBeGreaterThan(0);
    expect(fixture.nativeElement.textContent).toContain('Hook');
    expect(fixture.nativeElement.textContent).toContain('Content');
    expect(fixture.nativeElement.textContent).toContain('Guided Practice');
  });

  it('emits lesson completion from the final learner action without changing behavior', () => {
    spyOn(component.segmentCompleted, 'emit');
    component.isTeacherLed = false;
    fixture.detectChanges();

    const completeButton = Array.from(
      fixture.nativeElement.querySelectorAll('button'),
    )
      .find((button) => (button as HTMLButtonElement).textContent?.trim() === 'Complete Lesson') as HTMLButtonElement;

    completeButton.click();

    expect(component.segmentCompleted.emit).toHaveBeenCalled();
  });

  it('retains accessible labels for learner quiz interactions', () => {
    component.lesson = {
      ...component.lesson,
      activities: [{
        title: 'Check Your Understanding',
        type: 'quiz',
        content: JSON.stringify({
          question: 'Which claim is best supported?',
          options: ['Claim A', 'Claim B'],
        }),
      } as any],
    };

    fixture.detectChanges();

    const radiogroup = fixture.nativeElement.querySelector('[role="radiogroup"]') as HTMLElement;
    expect(radiogroup).not.toBeNull();
    expect(radiogroup.getAttribute('aria-label')).toBe('Quiz response options');
  });
});
