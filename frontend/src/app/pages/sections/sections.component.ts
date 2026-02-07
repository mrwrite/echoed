import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SectionsService } from '../../services/sections.service';
import { Section } from '../../models/section';
import { RouterModule } from '@angular/router';
import { ToastService } from '../../services/toast.service';

@Component({
  selector: 'app-sections',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './sections.component.html',
  styleUrl: './sections.component.scss'
})
export class SectionsComponent implements OnInit {
  sections: Section[] = [];
  name = '';
  courseVersionId = '';
  mode = 'remote';

  constructor(private sectionsService: SectionsService, private toastService: ToastService) {}

  ngOnInit(): void {
    this.loadSections();
  }

  loadSections(): void {
    this.sectionsService.listSections().subscribe(sections => {
      this.sections = sections;
    });
  }

  createSection(): void {
    if (!this.name || !this.courseVersionId) {
      return;
    }
    this.sectionsService.createSection({ name: this.name, course_version_id: this.courseVersionId, mode: this.mode }).subscribe(() => {
      this.toastService.show('Section created!', 'success');
      this.name = '';
      this.courseVersionId = '';
      this.loadSections();
    });
  }
}
