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
    component.goToStep(component.lessonSteps.length - 1);
    fixture.detectChanges();

    const text = fixture.nativeElement.textContent;
    expect(text).not.toContain('Teacher Notes');
    expect(text).toContain('Which source is more credible?');
  });

  it('shows educator-only fields in teacher-led mode', () => {
    component.isTeacherLed = true;
    fixture.detectChanges();
    component.goToStep(component.lessonSteps.length - 1);
    fixture.detectChanges();

    const text = fixture.nativeElement.textContent;
    expect(text).toContain('Teacher Notes');
    expect(text).toContain('Which source is more credible?');
  });

  it('keeps instructional sections in a clear learner step sequence', () => {
    component.isTeacherLed = false;
    fixture.detectChanges();

    const stepLabels = component.lessonSteps.map(step => step.label);
    expect(stepLabels).toContain('Hook');
    expect(stepLabels).toContain('Content');
    expect(stepLabels).toContain('Guided Practice');
    expect(fixture.nativeElement.textContent).toContain('Hook');
    expect(fixture.nativeElement.textContent).toContain('Open with a claim.');

    component.goToStep(1);
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Read the source text carefully.');
  });

  it('emits lesson completion from the final learner action without changing behavior', () => {
    spyOn(component.segmentCompleted, 'emit');
    component.isTeacherLed = false;
    fixture.detectChanges();
    component.goToStep(component.lessonSteps.length - 1);
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
    component.goToStep(component.lessonSteps.findIndex(step => step.kind === 'activity'));
    fixture.detectChanges();

    const radiogroup = fixture.nativeElement.querySelector('[role="radiogroup"]') as HTMLElement;
    expect(radiogroup).not.toBeNull();
    expect(radiogroup.getAttribute('aria-label')).toBe('Quiz response options');
  });

  it('keeps quiz activity input in place and announces validation before advancing', () => {
    component.lesson = {
      ...component.lesson,
      hook: undefined,
      content: undefined,
      guided_practice: undefined,
      discussion_questions: [],
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
    component.goToStep(component.lessonSteps.findIndex(step => step.kind === 'activity'));
    fixture.detectChanges();

    component.goToNextStep();
    fixture.detectChanges();

    expect(component.currentStep?.kind).toBe('activity');
    expect(fixture.nativeElement.textContent).toContain('Choose an answer before continuing');

    component.selectedOption = 'Claim A';
    fixture.detectChanges();
    component.goToNextStep();

    expect(component.activityErrorMessage).toBe('');
  });

  it('preserves next-activity flow for richer seeded activity patterns', () => {
    component.lesson = {
      ...component.lesson,
      activities: [
        { title: 'Story Prompt', type: 'story', content: 'Listen for a place-based clue.' } as any,
        { title: 'Reflection Prompt', type: 'reflection', content: 'What did you notice?' } as any,
        { title: 'Wrap Up', type: 'checkpoint', content: 'Share one key idea.' } as any,
      ],
    };

    fixture.detectChanges();
    component.goToStep(component.lessonSteps.findIndex(step => step.kind === 'activity'));
    fixture.detectChanges();

    let text = fixture.nativeElement.textContent;
    expect(text).toContain('Story Prompt');
    expect(text).toContain('Activity 1');

    component.goToNextActivity();
    fixture.detectChanges();

    text = fixture.nativeElement.textContent;
    expect(text).toContain('Reflection Prompt');
    expect(text).toContain('Activity 2');
  });

  it('renders a lesson activity progress bar for learner continuity', () => {
    component.lesson = {
      ...component.lesson,
      activities: [
        { title: 'Story Prompt', type: 'story', content: 'Listen for a clue.' } as any,
        { title: 'Wrap Up', type: 'checkpoint', content: 'Share one key idea.' } as any,
      ],
    };

    fixture.detectChanges();

    const progressbar = fixture.nativeElement.querySelector('[aria-label="Lesson progress"]') as HTMLElement;
    expect(progressbar).not.toBeNull();
    expect(progressbar.getAttribute('aria-valuenow')).toBe('17');
    expect(fixture.nativeElement.textContent).toContain('17% complete');
  });
});
