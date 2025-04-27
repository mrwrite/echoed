import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CourseWizardService } from '../../course-wizard.service';
import { CourseDraft } from '../../models/course-draft.model';


@Component({
  selector: 'step1-course-info',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './step1-course-info.component.html',
  styleUrl: './step1-course-info.component.scss'
})
export class Step1CourseInfoComponent {


  constructor(public courseWizardService: CourseWizardService) {}

 updateField(field: keyof CourseDraft, value: string) {
    this.courseWizardService.updateDraft({ [field]: value });
  }
}
