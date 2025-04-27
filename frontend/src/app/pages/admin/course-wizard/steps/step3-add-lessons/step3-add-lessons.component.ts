import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CourseWizardService } from '../../course-wizard.service';
import { LessonDraft } from '../../models/course-draft.model';
import { v4 as uuidv4 } from 'uuid';

@Component({
  selector: 'step3-add-lessons',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './step3-add-lessons.component.html',
  styleUrl: './step3-add-lessons.component.scss'
})
export class Step3AddLessonsComponent {
  selectedUnitId: string = '';
  lessonTitle: string = '';
  lessonType: 'text' | 'video' | 'quiz' = 'text';  
  lessonObjective: string = '';
  lessonDuration: number | null = null;

  constructor(public courseWizardService: CourseWizardService) {}

  addLesson() {
    if (!this.selectedUnitId || !this.lessonTitle.trim()) return;

    const draft = this.courseWizardService.draftValue;

    const newLesson: LessonDraft = {
      id: uuidv4(),
      title: this.lessonTitle.trim(),
      objective: this.lessonObjective.trim(),
      order: (draft.units.find(unit => unit.id === this.selectedUnitId)?.lessons.length || 0) + 1,
      duration_minutes: this.lessonDuration || 30,
      activities: []    
    };

    
    const updatedUnits = draft.units.map(unit => {
      if (unit.id === this.selectedUnitId) {
        return { ...unit, lessons: [...unit.lessons, newLesson] };
      }
      return unit;
    });

    this.courseWizardService.updateDraft({ units: updatedUnits });

    // Reset fields
    this.lessonTitle = '';
    this.lessonObjective = '';
    this.lessonDuration = null;
  }

  removeLesson(unitId: string, lessonId: string) {
    const draft = this.courseWizardService.draftValue;
    const updatedUnits = draft.units.map(unit => {
      if (unit.id === unitId) {
        return { ...unit, lessons: unit.lessons.filter(lesson => lesson.id !== lessonId) };
      }
      return unit;
    });

    this.courseWizardService.updateDraft({ units: updatedUnits });
  }
}
