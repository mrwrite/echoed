import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { Section } from '../../models/section';
import { OrganizationService } from '../../services/organization.service';

@Component({
  selector: 'app-organization-sections',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, EchoLoadingStateComponent, EchoStatePanelComponent],
  templateUrl: './organization-sections.component.html',
  styleUrl: './organization-sections.component.scss',
})
export class OrganizationSectionsComponent implements OnInit {
  sections: Section[] = [];
  searchTerm = '';
  modeFilter = '';
  loading = true;
  loadError = '';

  constructor(private readonly organizations: OrganizationService) {}

  ngOnInit(): void { this.load(); }

  get modes(): string[] { return [...new Set(this.sections.map(section => section.mode))].sort(); }

  get filteredSections(): Section[] {
    const search = this.searchTerm.trim().toLowerCase();
    return this.sections.filter(section =>
      (!this.modeFilter || section.mode === this.modeFilter) &&
      (!search || section.name.toLowerCase().includes(search))
    );
  }

  load(): void {
    const orgId = this.organizations.getActiveOrgId();
    this.loading = true;
    this.loadError = '';
    if (!orgId) {
      this.loading = false;
      this.loadError = 'Choose an active organization before reviewing classes.';
      return;
    }
    this.organizations.getSections(orgId).subscribe({
      next: sections => { this.sections = sections; this.loading = false; },
      error: () => { this.sections = []; this.loading = false; this.loadError = 'We could not load organization classes. No class data was changed.'; },
    });
  }

  label(value: string): string { return value.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase()); }
}
