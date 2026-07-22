import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { switchMap } from 'rxjs/operators';

import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { OrganizationMember } from '../../models/organization';
import { Enrollment, Section, SectionSummary } from '../../models/section';
import { OrganizationService } from '../../services/organization.service';
import { SectionsService } from '../../services/sections.service';

@Component({
  selector: 'app-organization-section-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, EchoLoadingStateComponent, EchoStatePanelComponent],
  templateUrl: './organization-section-detail.component.html',
  styleUrl: './organization-section-detail.component.scss',
})
export class OrganizationSectionDetailComponent implements OnInit {
  section?: Section;
  roster: Enrollment[] = [];
  members: OrganizationMember[] = [];
  summary?: SectionSummary;
  loading = true;
  loadError = '';

  constructor(
    private readonly route: ActivatedRoute,
    private readonly organizations: OrganizationService,
    private readonly sectionsService: SectionsService,
  ) {}

  ngOnInit(): void { this.load(); }

  load(): void {
    const sectionId = this.route.snapshot.paramMap.get('sectionId') || '';
    const orgId = this.organizations.getActiveOrgId();
    this.loading = true;
    this.loadError = '';
    if (!orgId || !sectionId) {
      this.loading = false;
      this.loadError = 'This class link is incomplete or no active organization is selected.';
      return;
    }
    this.organizations.getSections(orgId).pipe(
      switchMap(sections => {
        this.section = sections.find(section => section.id === sectionId);
        if (!this.section) throw new Error('section-not-in-organization');
        return forkJoin({
          roster: this.sectionsService.getRoster(sectionId),
          summary: this.sectionsService.getSectionSummary(sectionId),
          members: this.organizations.getMembers(orgId),
        });
      }),
    ).subscribe({
      next: result => {
        this.roster = result.roster;
        this.summary = result.summary;
        this.members = result.members;
        this.loading = false;
      },
      error: () => {
        this.section = undefined;
        this.loading = false;
        this.loadError = 'This class is unavailable in the active organization, or its roster could not be loaded.';
      },
    });
  }

  memberName(enrollment: Enrollment): string {
    return this.members.find(member => member.user_id === enrollment.user_id)?.display_name || 'Member profile unavailable';
  }

  label(value: string): string { return value.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase()); }
}
