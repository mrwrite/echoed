import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CourseWizardService } from '../../course-wizard.service';
import { CoursesService } from '../../../../../services/courses.service';
import { Router, ActivatedRoute } from '@angular/router';
import { v4 as uuidv4 } from 'uuid';

@Component({
  selector: 'step4-review-save',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './step4-review-save.component.html',
  styleUrl: './step4-review-save.component.scss'
})
export class Step4ReviewSaveComponent implements OnInit {
  isSaving: boolean = false;
  errorMessage: string = '';
  courseId: string | null = null; // For editing an existing course
  addingActivityUnitId: string | null = null;
  addingActivityLessonId: string | null = null;
  newActivityType: 'video' | 'story' | 'song' | 'coloring' | 'discussion' | 'text' = 'text';
  newActivityTitle: string = '';
  newActivityContent: string = '';
  newColoringFile: File | null = null;

  constructor(public courseWizardService: CourseWizardService,
              private coursesService: CoursesService,
              private router: Router,
              private route: ActivatedRoute) {}

              
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
          console.log('Course updated successfully!');
          // ✅ Redirect to course management page (or success screen)
          //this.router.navigate(['/home']);
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
          console.log('Course saved successfully!');
          // ✅ Redirect to course management page (or success screen)
          this.router.navigate(['/admin/courses']);
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
  }
  
  cancelAddActivity() {
    this.addingActivityUnitId = null;
    this.addingActivityLessonId = null;
    this.newColoringFile = null;
  }

  onColoringFileSelected(event: any) {
    const file = event.target.files && event.target.files.length > 0 ? event.target.files[0] : null;
    this.newColoringFile = file;
  }
  
  confirmAddActivity() {
    if (!this.newActivityTitle.trim()) return;

    const draft = this.courseWizardService.draftValue;
    const addActivity = (content: string) => {
      const updatedUnits = draft.units.map(unit => {
        if (unit.id === this.addingActivityUnitId) {
          const updatedLessons = unit.lessons.map(lesson => {
            if (lesson.id === this.addingActivityLessonId) {
              const newActivity = {
                id: uuidv4(),
                type: this.newActivityType,
                title: this.newActivityTitle.trim(),
                content: content,
                order: lesson.activities.length + 1
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
