import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CourseWizardService } from '../../course-wizard.service';
import { UnitDraft } from '../../models/course-draft.model';

@Component({
  selector: 'step2-add-units',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './step2-add-units.component.html',
  styleUrl: './step2-add-units.component.scss'
})
export class Step2AddUnitsComponent {
  unitTitle: string = '';
  unitDescription: string = '';

  constructor(public courseWizardService: CourseWizardService) {}

  addUnit() {
    if (!this.unitTitle.trim()) return; // Validation: ignore blank titles

    const newUnit: UnitDraft = {
      id: crypto.randomUUID(),
      title: this.unitTitle.trim(),
      content: this.unitDescription.trim(),
      order: this.courseWizardService.draftValue.units.length + 1,
      lessons: []
    };

    const updatedUnits = [...this.courseWizardService.draftValue.units, newUnit];
    this.courseWizardService.updateDraft({ units: updatedUnits });

    this.unitTitle = '';
    this.unitDescription = '';
  }

  removeUnit(id: string) {
    const updatedUnits = this.courseWizardService.draftValue.units.filter(unit => unit.id !== id);
    this.courseWizardService.updateDraft({ units: updatedUnits });
  }
}
