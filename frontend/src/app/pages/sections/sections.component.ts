import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';

import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { Section, SectionSummary } from '../../models/section';
import { SectionsService } from '../../services/sections.service';
import { ToastService } from '../../services/toast.service';

@Component({
  selector: 'app-sections',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, EchoLoadingStateComponent, EchoStatePanelComponent],
  templateUrl: './sections.component.html',
  styleUrl: './sections.component.scss'
})
export class SectionsComponent implements OnInit {
  sections: Section[] = [];
  summaries: Record<string, SectionSummary> = {};
  name = '';
  courseVersionId = '';
  mode = 'remote';
  searchTerm = '';
  loading = true;
  creating = false;
  loadError = '';
  formError = '';

  constructor(private sectionsService: SectionsService, private toastService: ToastService) {}

  ngOnInit(): void {
    this.loadSections();
  }

  get filteredSections(): Section[] {
    const search = this.searchTerm.trim().toLowerCase();
    if (!search) {
      return this.sections;
    }
    return this.sections.filter(section =>
      section.name.toLowerCase().includes(search) ||
      section.mode.toLowerCase().includes(search)
    );
  }

  loadSections(): void {
    this.loading = true;
    this.loadError = '';
    this.sectionsService.listSections().subscribe({
      next: (sections) => {
        this.sections = sections;
        this.loading = false;
        this.loadSummaries();
      },
      error: () => {
        this.sections = [];
        this.summaries = {};
        this.loading = false;
        this.loadError = 'We could not load your classes. No class data was changed.';
      },
    });
  }

  createSection(): void {
    this.formError = '';
    if (!this.name.trim() || !this.courseVersionId.trim()) {
      this.formError = 'Class name and course version ID are required by the current section API.';
      return;
    }

    this.creating = true;
    this.sectionsService.createSection({
      name: this.name.trim(),
      course_version_id: this.courseVersionId.trim(),
      mode: this.mode,
    }).subscribe({
      next: () => {
        this.toastService.show('Class created.', 'success');
        this.name = '';
        this.courseVersionId = '';
        this.mode = 'remote';
        this.creating = false;
        this.loadSections();
      },
      error: (error) => {
        this.creating = false;
        this.formError = error?.error?.detail || 'We could not create this class. No learners were enrolled.';
      },
    });
  }

  learnerCount(section: Section): number {
    return this.summaries[section.id]?.totals.enrolled ?? 0;
  }

  lessonCount(section: Section): number {
    return this.summaries[section.id]?.totals.lessons_completed ?? 0;
  }

  private loadSummaries(): void {
    if (this.sections.length === 0) {
      this.summaries = {};
      return;
    }

    forkJoin(
      this.sections.map(section =>
        this.sectionsService.getSectionSummary(section.id).pipe(catchError(() => of(undefined)))
      )
    ).subscribe((summaries) => {
      this.summaries = summaries.reduce((map, summary) => {
        if (summary) {
          map[summary.section_id] = summary;
        }
        return map;
      }, {} as Record<string, SectionSummary>);
    });
  }
}
