import { Component, Input, Output, EventEmitter, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { Lesson } from '../models/lesson';
import { ColoringCanvasComponent } from '../components/coloring-canvas/coloring-canvas.component';
import { StorybookViewerComponent } from '../components/storybook-viewer/storybook-viewer.component';
import { AfricaMapExplorerComponent, AfricaMapExplorerData } from '../components/africa-map-explorer/africa-map-explorer.component';

type LessonStep =
  | { kind: 'overview'; label: string; title: string }
  | { kind: 'instruction'; label: string; title: string; content: string }
  | { kind: 'activity'; label: string; activityIndex: number }
  | { kind: 'discussion'; label: string; title: string; questions: string[] }
  | { kind: 'sources'; label: string; title: string };

@Component({
  selector: 'echoed-lesson-viewer',
  standalone: true,
  imports: [CommonModule, FormsModule, ColoringCanvasComponent, StorybookViewerComponent, AfricaMapExplorerComponent],
  templateUrl: './lesson-viewer.component.html',
  styleUrl: './lesson-viewer.component.scss'
})
export class LessonViewerComponent implements OnChanges {
  constructor(private sanitizer: DomSanitizer) {}

  @Input() lesson!: Lesson;
  @Input() isTeacherLed: boolean = false;
  @Output() segmentCompleted = new EventEmitter<void>();

  currentActivityIndex = 0;
  currentStepIndex = 0;
  reflectionResponse = '';
  selectedOption = '';

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['lesson']) {
      this.currentActivityIndex = 0;
      this.currentStepIndex = 0;
      this.reflectionResponse = '';
      this.selectedOption = '';
    }
  }

  get currentActivity() {
    if (this.currentStep?.kind !== 'activity') {
      return null;
    }
    return this.orderedActivities[this.currentStep.activityIndex] ?? null;
  }

  get activityCount(): number {
    return this.orderedActivities.length;
  }

  get orderedActivities() {
    return [...(this.lesson?.activities || [])].sort((left, right) => {
      const leftOrder = left.order ?? Number.MAX_SAFE_INTEGER;
      const rightOrder = right.order ?? Number.MAX_SAFE_INTEGER;
      if (leftOrder !== rightOrder) {
        return leftOrder - rightOrder;
      }
      return 0;
    });
  }

  get lessonSteps(): LessonStep[] {
    const steps: LessonStep[] = [];

    if (this.lesson?.objective || this.lesson?.learning_objectives || (this.lesson?.key_concepts?.length ?? 0) > 0) {
      steps.push({ kind: 'overview', label: 'Goals', title: 'What you will learn' });
    }

    steps.push(
      ...this.instructionalSections
        .filter(section => section.content)
        .map(section => ({
          kind: 'instruction' as const,
          label: section.label,
          title: section.label,
          content: section.content || '',
        })),
    );

    this.orderedActivities.forEach((activity, index) => {
      steps.push({
        kind: 'activity',
        label: `Activity ${index + 1}`,
        activityIndex: index,
      });
    });

    if ((this.lesson?.discussion_questions?.length ?? 0) > 0) {
      steps.push({
        kind: 'discussion',
        label: 'Discuss',
        title: 'Talk it through',
        questions: this.lesson.discussion_questions || [],
      });
    }

    if ((this.lesson?.sources?.length ?? 0) > 0) {
      steps.push({
        kind: 'sources',
        label: 'Sources',
        title: 'Where this lesson comes from',
      });
    }

    return steps;
  }

  get currentStep(): LessonStep | null {
    return this.lessonSteps[this.currentStepIndex] ?? null;
  }

  get stepCount(): number {
    return this.lessonSteps.length;
  }

  get activityProgressPercent(): number {
    if (!this.stepCount) {
      return 0;
    }

    return Math.round(((this.currentStepIndex + 1) / this.stepCount) * 100);
  }

  get isLastActivity(): boolean {
    return this.currentStepIndex === this.stepCount - 1;
  }

  get isFirstStep(): boolean {
    return this.currentStepIndex === 0;
  }

  get currentStepLabel(): string {
    return this.currentStep?.label || 'Lesson';
  }

  get currentStepTitle(): string {
    const step = this.currentStep;
    if (!step) {
      return '';
    }
    if (step.kind === 'activity') {
      return this.currentActivity?.title || 'Activity';
    }
    return step.title;
  }

  get currentInstructionContent(): string {
    return this.currentStep?.kind === 'instruction' ? this.currentStep.content : '';
  }

  get currentDiscussionQuestions(): string[] {
    return this.currentStep?.kind === 'discussion' ? this.currentStep.questions : [];
  }

  get instructionalSections(): Array<{ label: string; content?: string }> {
    return [
      { label: 'Hook', content: this.lesson?.hook },
      { label: 'Content', content: this.lesson?.content },
      { label: 'Guided Practice', content: this.lesson?.guided_practice },
      { label: 'Independent Practice', content: this.lesson?.independent_practice },
      { label: 'Assessment', content: this.lesson?.assessment },
    ].filter(section => !!section.content);
  }

  get showEducatorContent(): boolean {
    return this.isTeacherLed;
  }

  goToNextActivity(): void {
    this.goToNextStep();
  }

  goToStep(index: number): void {
    if (index < 0 || index >= this.stepCount) {
      return;
    }
    this.currentStepIndex = index;
    this.syncActivityIndex();
    this.resetStepInputs();
  }

  goToNextStep(): void {
    if (this.currentStepIndex < this.stepCount - 1) {
      this.currentStepIndex++;
      this.syncActivityIndex();
      this.resetStepInputs();
    }
  }

  goToPreviousStep(): void {
    if (this.currentStepIndex > 0) {
      this.currentStepIndex--;
      this.syncActivityIndex();
      this.resetStepInputs();
    }
  }

  private syncActivityIndex(): void {
    if (this.currentStep?.kind === 'activity') {
      this.currentActivityIndex = this.currentStep.activityIndex;
    }
  }

  private resetStepInputs(): void {
    this.reflectionResponse = '';
    this.selectedOption = '';
  }

  isYouTubeLink(url: string): boolean {
    return url.includes('youtube.com') || url.includes('youtu.be');
  }

  getYouTubeEmbedUrl(url: string): SafeResourceUrl {
    const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([\w-]+)/);
    const videoId = match && match[1] ? match[1] : '';
    return this.sanitizer.bypassSecurityTrustResourceUrl(`https://www.youtube.com/embed/${videoId}`);
  }

  get quizPayload() {
    const content = this.currentActivity?.content;
    if (!content) {
      return null;
    }
    try {
      const parsed = JSON.parse(content);
      if (parsed && parsed.question && Array.isArray(parsed.options)) {
        return parsed;
      }
    } catch {
      return null;
    }
    return null;
  }

  get mapPayload(): AfricaMapExplorerData | null {
    const content = this.currentActivity?.content;
    if (!content) {
      return null;
    }
    try {
      const parsed = JSON.parse(content);
      if (parsed && Array.isArray(parsed.regions)) {
        return parsed as AfricaMapExplorerData;
      }
    } catch {
      return null;
    }
    return null;
  }

  onMarkComplete(): void {
    // Emit when lesson segment is completed (for updating progress)
    this.segmentCompleted.emit();
  }
}
