import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Observable, Subscription } from 'rxjs';

import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { Artifact, KnowledgeSource, Product, Project } from '../../models/v2-platform.model';
import { V2PlatformService } from '../../services/v2-platform.service';

type StudioLibraryMode = 'projects' | 'content' | 'courses' | 'programs' | 'sources' | 'drafts' | 'publishing';

interface StudioLibraryItem {
  id: string;
  title: string;
  summary: string;
  status: string;
  type: string;
  context: string;
  detailRoute?: string;
}

const MODE_COPY: Record<StudioLibraryMode, { eyebrow: string; title: string; intro: string; empty: string }> = {
  projects: { eyebrow: 'Curriculum organization', title: 'Projects', intro: 'Organize related sources, content drafts, and learning offerings within a scoped curriculum project.', empty: 'No curriculum projects are available in the current organization scope.' },
  content: { eyebrow: 'Learning content', title: 'Content library', intro: 'Review the course, path, certification, and resource wrappers currently available to Studio.', empty: 'No learning offerings are available in the current organization scope.' },
  courses: { eyebrow: 'Course stewardship', title: 'Course wrappers', intro: 'Inspect course-backed publishing and review records. Full course graph editing is not supported for content administrators by the current APIs.', empty: 'No course wrappers are available in the current organization scope.' },
  programs: { eyebrow: 'Learning sequences', title: 'Programs and learning paths', intro: 'Inspect program-backed and learning-path wrappers. Course membership and ordering remain read-only until supported authoring APIs exist.', empty: 'No program or learning-path wrappers are available in the current organization scope.' },
  sources: { eyebrow: 'Evidence and attribution', title: 'Source library', intro: 'Review source identity, citation text, and project usage recorded by the current source-wrapper API.', empty: 'No source records are available in the current organization scope.' },
  drafts: { eyebrow: 'Prepared content', title: 'Content drafts', intro: 'Inspect source-linked outlines, guides, lesson drafts, and other reviewable content outputs.', empty: 'No content drafts are available in the current organization scope.' },
  publishing: { eyebrow: 'Availability and release', title: 'Publishing states', intro: 'Review wrapper status and visibility. Learner lesson governance remains separately authoritative.', empty: 'No publishable learning offerings are available in the current organization scope.' },
};

@Component({
  selector: 'app-studio-library',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, EchoLoadingStateComponent, EchoStatePanelComponent],
  templateUrl: './studio-library.component.html',
  styleUrl: './studio-library.component.scss',
})
export class StudioLibraryComponent implements OnInit, OnDestroy {
  mode: StudioLibraryMode = 'content';
  copy = MODE_COPY.content;
  items: StudioLibraryItem[] = [];
  loading = true;
  failed = false;
  search = '';
  statusFilter = 'all';
  private readonly subscriptions = new Subscription();

  constructor(private readonly route: ActivatedRoute, private readonly platform: V2PlatformService) {}

  ngOnInit(): void {
    this.subscriptions.add(this.route.data.subscribe(data => {
      this.mode = (data['mode'] as StudioLibraryMode) || 'content';
      this.copy = MODE_COPY[this.mode];
      this.load();
    }));
  }

  ngOnDestroy(): void { this.subscriptions.unsubscribe(); }

  get statusOptions(): string[] { return [...new Set(this.items.map(item => item.status))].sort(); }
  get filteredItems(): StudioLibraryItem[] {
    const query = this.search.trim().toLowerCase();
    return this.items.filter(item => {
      const matchesSearch = !query || [item.title, item.summary, item.type, item.context].some(value => value.toLowerCase().includes(query));
      const matchesStatus = this.statusFilter === 'all' || item.status === this.statusFilter;
      return matchesSearch && matchesStatus;
    });
  }
  get resultText(): string { return `${this.filteredItems.length} ${this.filteredItems.length === 1 ? 'item' : 'items'} shown`; }

  load(): void {
    this.loading = true;
    this.failed = false;
    let request: Observable<Array<Project | KnowledgeSource | Artifact | Product>>;
    if (this.mode === 'projects') request = this.platform.getProjects();
    else if (this.mode === 'sources') request = this.platform.getKnowledgeSources();
    else if (this.mode === 'drafts') request = this.platform.getArtifacts();
    else request = this.platform.getProducts();

    this.subscriptions.add(request.subscribe({
      next: records => {
        this.items = this.mapRecords(records);
        this.loading = false;
      },
      error: () => { this.failed = true; this.loading = false; },
    }));
  }

  label(value: string): string { return value.replace(/_/g, ' ').replace(/\b\w/g, character => character.toUpperCase()); }
  statusClass(status: string): string {
    if (['published', 'approved', 'active', 'available'].includes(status)) return 'studio-status--success';
    if (['rejected', 'archived', 'blocked'].includes(status)) return 'studio-status--danger';
    if (['draft', 'in_review', 'needs_changes', 'not_reviewed'].includes(status)) return 'studio-status--warning';
    return '';
  }

  private mapRecords(records: Array<Project | KnowledgeSource | Artifact | Product>): StudioLibraryItem[] {
    if (this.mode === 'projects') return (records as Project[]).map(item => ({ id: item.id, title: item.name, summary: item.description || 'No project description has been provided.', status: item.status, type: 'Curriculum project', context: 'Sources and drafts are managed from the project detail.', detailRoute: `/studio/projects/${item.id}` }));
    if (this.mode === 'sources') return (records as KnowledgeSource[]).map(item => ({ id: item.id, title: item.title, summary: item.citation || item.uri || 'No citation or reference has been recorded.', status: item.status, type: this.label(item.source_type), context: item.citation ? 'Citation recorded' : 'Citation needs attention' }));
    if (this.mode === 'drafts') return (records as Artifact[]).map(item => ({ id: item.id, title: item.title, summary: item.body || item.uri || 'No preview content has been recorded.', status: item.review_state || item.status, type: this.label(item.artifact_type), context: item.knowledge_source_id ? 'Source record linked' : 'No source record linked', detailRoute: `/studio/drafts/${item.id}` }));

    let products = records as Product[];
    if (this.mode === 'courses') products = products.filter(item => item.product_type === 'course' || !!item.course_id);
    if (this.mode === 'programs') products = products.filter(item => item.product_type === 'learning_path' || !!item.program_id);
    return products.map(item => ({
      id: item.id,
      title: item.title,
      summary: item.description || item.subtitle || 'No learner-facing description has been provided.',
      status: item.status,
      type: this.label(item.product_type),
      context: `${this.label(item.review_state)} review; ${this.label(item.visibility)} visibility`,
      detailRoute: `/studio/content/${item.id}`,
    }));
  }
}
