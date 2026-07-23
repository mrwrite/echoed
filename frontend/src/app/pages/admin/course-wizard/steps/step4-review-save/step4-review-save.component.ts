import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CdkDragDrop, moveItemInArray, DragDropModule } from '@angular/cdk/drag-drop';
import { CourseWizardService } from '../../course-wizard.service';
import { ActivityDraft } from '../../models/course-draft.model';
import { CoursesService } from '../../../../../services/courses.service';
import { Router, ActivatedRoute } from '@angular/router';
import { ToastService } from '../../../../../services/toast.service';

@Component({
  selector: 'step4-review-save',
  standalone: true,
  imports: [CommonModule, FormsModule, DragDropModule],
  templateUrl: './step4-review-save.component.html',
  styleUrl: './step4-review-save.component.scss'
})
export class Step4ReviewSaveComponent implements OnInit {
  isSaving: boolean = false;
  errorMessage: string = '';
  courseId: string | null = null; // For editing an existing course
  addingActivityUnitId: string | null = null;
  addingActivityLessonId: string | null = null;
  newActivityType: 'video' | 'story' | 'storybook' | 'song' | 'coloring' | 'discussion' | 'text' = 'text';
  newActivityTitle: string = '';
  newActivityContent: string = '';
  newColoringFile: File | null = null;
  storybookPages: { id: string; imageUrl: string; order: number; file?: File | null }[] = [];

  constructor(public courseWizardService: CourseWizardService,
              private coursesService: CoursesService,
              private router: Router,
              private route: ActivatedRoute,
              private toastService: ToastService) {}

              
  ngOnInit() {
    this.courseId = this.route.snapshot.paramMap.get('courseId');
  }
  
  saveCourse() {
    this.isSaving = true;
    this.errorMessage = '';

    const draft = this.courseWizardService.draftValue;

    if (this.courseId) {
      this.coursesService.updateCourse(this.courseId, draft).subscribe({
        next: () => {
          this.isSaving = false;
          this.toastService.show('Course updated successfully', 'success');
          this.router.navigate(['/home/admin/courses']);
        },
        error: (error) => {
          this.isSaving = false;
          console.error('Error updating course:', error);
          this.errorMessage = 'Something went wrong. Please try again.';
        }
      });
    } else {

      this.coursesService.createCourse(draft).subscribe({
        next: () => {
          this.isSaving = false;
          this.toastService.show('Course created successfully', 'success');
          this.courseWizardService.resetDraft();
          this.router.navigate(['/home/admin/courses']);
        },
        error: (error) => {
          this.isSaving = false;
          console.error('Error saving course:', error);
          this.errorMessage = 'Something went wrong. Please try again.';
        }
      });

    }
   
  }

  startAddingActivity(unitId: string, lessonId: string) {
    this.addingActivityUnitId = unitId;
    this.addingActivityLessonId = lessonId;
    this.newActivityType = 'text';
    this.newActivityTitle = '';
    this.newActivityContent = '';
    this.newColoringFile = null;
    this.storybookPages = [];
  }
  
  cancelAddActivity() {
    this.addingActivityUnitId = null;
    this.addingActivityLessonId = null;
    this.newColoringFile = null;
    this.storybookPages = [];
  }

  onColoringFileSelected(event: any) {
    const file = event.target.files && event.target.files.length > 0 ? event.target.files[0] : null;
    this.newColoringFile = file;
  }

  onStorybookFileSelected(event: any, page: { id: string; imageUrl: string; order: number; file?: File | null }) {
    const file = event.target.files && event.target.files.length > 0 ? event.target.files[0] : null;
    if (file) {
      this.coursesService.uploadStorybookPage(file).subscribe({
        next: res => page.imageUrl = res.file_path,
        error: err => {
          console.error('Error uploading storybook page:', err);
          this.errorMessage = 'Failed to upload storybook page.';
        }
      });
    }
  }

  addStorybookPage() {
    this.storybookPages.push({ id: crypto.randomUUID(), imageUrl: '', order: this.storybookPages.length + 1, file: null });
  }

  removeStorybookPage(id: string) {
    this.storybookPages = this.storybookPages.filter(p => p.id !== id);
  }

  dropPage(event: CdkDragDrop<{ id: string; imageUrl: string; order: number }[]>) {
    moveItemInArray(this.storybookPages, event.previousIndex, event.currentIndex);
    this.storybookPages.forEach((p, idx) => p.order = idx + 1);
  }

  dropActivity(event: CdkDragDrop<ActivityDraft[]>, unitId: string, lessonId: string) {
    const draft = this.courseWizardService.draftValue;
    const updatedUnits = draft.units.map(unit => {
      if (unit.id === unitId) {
        const updatedLessons = unit.lessons.map(lesson => {
          if (lesson.id === lessonId) {
            const updatedActivities = [...lesson.activities];
            moveItemInArray(updatedActivities, event.previousIndex, event.currentIndex);
            updatedActivities.forEach((a, idx) => a.order = idx + 1);
            return { ...lesson, activities: updatedActivities };
          }
          return lesson;
        });
        return { ...unit, lessons: updatedLessons };
      }
      return unit;
    });

    this.courseWizardService.updateDraft({ units: updatedUnits });
  }
  
  confirmAddActivity() {
    if (!this.newActivityTitle.trim()) return;

    const draft = this.courseWizardService.draftValue;
    const addActivity = (content: string) => {
      const updatedUnits = draft.units.map(unit => {
        if (unit.id === this.addingActivityUnitId) {
          const updatedLessons = unit.lessons.map(lesson => {
            if (lesson.id === this.addingActivityLessonId) {
              const newActivity: any = {
                id: crypto.randomUUID(),
                type: this.newActivityType,
                title: this.newActivityTitle.trim(),
                content: content,
                order: lesson.activities.length + 1,
                pages: this.storybookPages.map(p => ({ image_url: p.imageUrl, order: p.order }))
              };
              return { ...lesson, activities: [...lesson.activities, newActivity] };
            }
            return lesson;
          });

          return { ...unit, lessons: updatedLessons };
        }
        return unit;
      });

      this.courseWizardService.updateDraft({ units: updatedUnits });
      this.cancelAddActivity();
    };

    if (this.newActivityType === 'coloring' && this.newColoringFile) {
      this.coursesService.uploadColoring(this.newColoringFile).subscribe({
        next: res => addActivity(res.file_path),
        error: err => {
          console.error('Error uploading coloring page:', err);
          this.errorMessage = 'Failed to upload coloring page.';
        }
      });
    } else if (this.newActivityType === 'storybook') {
      addActivity('');
    } else {
      addActivity(this.newActivityContent.trim());
    }
  }

  removeActivity(unitId: string, lessonId: string, activityId: string) {
    const draft = this.courseWizardService.draftValue;
  
    const updatedUnits = draft.units.map(unit => {
      if (unit.id === unitId) {
        const updatedLessons = unit.lessons.map(lesson => {
          if (lesson.id === lessonId) {
            return { ...lesson, activities: lesson.activities.filter(a => a.id !== activityId) };
          }
          return lesson;
        });
  
        return { ...unit, lessons: updatedLessons };
      }
      return unit;
    });
  
    this.courseWizardService.updateDraft({ units: updatedUnits });
  }
}
