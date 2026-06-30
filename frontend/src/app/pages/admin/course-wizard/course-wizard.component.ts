import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CourseWizardService } from './course-wizard.service';
import { CourseDraft } from './models/course-draft.model';
import { ActivatedRoute, Router } from '@angular/router';

// Import your step components
import { Step1CourseInfoComponent } from './steps/step1-course-info/step1-course-info.component';
import { Step2AddUnitsComponent } from './steps/step2-add-units/step2-add-units.component';
import { Step3AddLessonsComponent } from './steps/step3-add-lessons/step3-add-lessons.component';
import { Step4ReviewSaveComponent } from './steps/step4-review-save/step4-review-save.component';
import { CoursesService } from '../../../services/courses.service';

@Component({
  selector: 'course-wizard',
  standalone: true,
  imports: [
    CommonModule,
    Step1CourseInfoComponent,
    Step2AddUnitsComponent,
    Step3AddLessonsComponent,
    Step4ReviewSaveComponent
  ],
  providers: [], // Add the service to the providers array
  templateUrl: './course-wizard.component.html',
  styleUrl: './course-wizard.component.scss'
})
export class CourseWizardComponent implements OnInit {
  currentStep: number = 1; // 1-based steps
  totalSteps: number = 4;
  courseId: string | null = null; // For editing an existing course
  isEditMode: boolean = false; // Flag to check if in edit mode
  isLoading: boolean = false; // Flag to show loading spinner

  constructor(public courseWizardService: CourseWizardService,
    private courseService: CoursesService,
    private router: Router,
    private route: ActivatedRoute){}

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      this.courseId = params.get('courseId');
  
      if (this.courseId) {
        this.isEditMode = true;
        this.isLoading = true;

        this.courseService.getCourseById(this.courseId).subscribe({
          next: (course) => {
            this.courseWizardService.updateDraft(course);
            this.isLoading = false;
          },
          error: (err) => {
            console.error('Error loading course', err);
            this.router.navigate(['/home']); // fallback
          }
      });

      } else {
        this.courseWizardService.resetDraft(); // Start fresh
        this.isEditMode = false;
        this.isLoading = false;
      }
    });
  }

  nextStep() {
    if (this.currentStep < this.totalSteps) {
      this.currentStep++;
    }
  }

  previousStep() {
    if (this.currentStep > 1) {
      this.currentStep--;
    }
  }

  goToStep(step: number) {
    if (step >= 1 && step <= this.totalSteps) {
      this.currentStep = step;
    }
  }

  saveDraft() {
    const draft = this.courseWizardService.draftValue;
  
    if (this.isEditMode && this.courseId) {
      // PUT update existing course
      this.courseService.updateCourse(this.courseId, draft).subscribe({
        next: () => {
          this.router.navigate(['/home']); // Redirect back to dashboard
        },
        error: (err) => {
          console.error('Error updating course', err);
        }
      });
    } else {
      // POST create new course
      this.courseService.createCourse(draft).subscribe({
        next: () => {
          this.router.navigate(['/home']); // Redirect back to dashboard
        },
        error: (err) => {
          console.error('Error creating course', err);
        }
      });
    }
  }
  
}
