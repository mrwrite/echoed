import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { forkJoin, Subscription } from 'rxjs';

import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { Artifact, KnowledgeSource, Product, Project } from '../../models/v2-platform.model';
import { V2PlatformService } from '../../services/v2-platform.service';

@Component({
  selector: 'app-studio-project-detail',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, EchoLoadingStateComponent, EchoStatePanelComponent],
  templateUrl: './studio-project-detail.component.html',
  styleUrl: './studio-project-detail.component.scss',
})
export class StudioProjectDetailComponent implements OnInit, OnDestroy {
  readonly sourceTypes = ['repository', 'document', 'pdf', 'url', 'transcript', 'upload', 'manual_note', 'lesson_source'];
  readonly draftTypes = ['outline', 'documentation', 'guide', 'checklist', 'source_map', 'export_bundle', 'assessment_seed', 'lesson_draft'];
  project?: Project;
  products: Product[] = [];
  sources: KnowledgeSource[] = [];
  drafts: Artifact[] = [];
  loading = true;
  failed = false;
  savingSource = false;
  savingDraft = false;
  sourceError = '';
  draftError = '';
  statusMessage = '';
  sourceForm = { title: '', type: 'document', uri: '', citation: '' };
  draftForm = { title: '', type: 'lesson_draft', productId: '', sourceId: '', body: '' };
  private projectId = '';
  private readonly subscriptions = new Subscription();

  constructor(private readonly route: ActivatedRoute, private readonly platform: V2PlatformService) {}
  ngOnInit(): void { this.projectId = this.route.snapshot.paramMap.get('projectId') || ''; this.load(); }
  ngOnDestroy(): void { this.subscriptions.unsubscribe(); }

  load(): void {
    if (!this.projectId) { this.failed = true; this.loading = false; return; }
    this.loading = true; this.failed = false;
    this.subscriptions.add(forkJoin({ project: this.platform.getProject(this.projectId), products: this.platform.getProducts({ projectId: this.projectId }), sources: this.platform.getProjectKnowledgeSources(this.projectId), drafts: this.platform.getProjectArtifacts(this.projectId) }).subscribe({
      next: result => { this.project = result.project; this.products = result.products; this.sources = result.sources; this.drafts = result.drafts; this.loading = false; },
      error: () => { this.failed = true; this.loading = false; },
    }));
  }

  createSource(): void {
    if (!this.project || !this.sourceForm.title.trim() || this.savingSource) return;
    this.savingSource = true; this.sourceError = ''; this.statusMessage = '';
    this.subscriptions.add(this.platform.createKnowledgeSource({ workspace_id: this.project.workspace_id, project_id: this.project.id, title: this.sourceForm.title.trim(), source_type: this.sourceForm.type, uri: this.sourceForm.uri.trim() || null, citation: this.sourceForm.citation.trim() || null, status: 'active' }).subscribe({
      next: source => { this.sources = [...this.sources, source]; this.sourceForm = { title: '', type: 'document', uri: '', citation: '' }; this.savingSource = false; this.statusMessage = `Source “${source.title}” added to this project.`; },
      error: () => { this.savingSource = false; this.sourceError = 'The source was not added. Your entries remain available to review.'; },
    }));
  }

  createDraft(): void {
    if (!this.project || !this.draftForm.title.trim() || this.savingDraft) return;
    this.savingDraft = true; this.draftError = ''; this.statusMessage = '';
    this.subscriptions.add(this.platform.createArtifact({ workspace_id: this.project.workspace_id, project_id: this.project.id, product_id: this.draftForm.productId || null, knowledge_source_id: this.draftForm.sourceId || null, artifact_type: this.draftForm.type, title: this.draftForm.title.trim(), body: this.draftForm.body.trim() || null, status: 'draft', review_state: 'review_required' }).subscribe({
      next: draft => { this.drafts = [...this.drafts, draft]; this.draftForm = { title: '', type: 'lesson_draft', productId: '', sourceId: '', body: '' }; this.savingDraft = false; this.statusMessage = `Draft “${draft.title}” created. It is not learner-visible.`; },
      error: () => { this.savingDraft = false; this.draftError = 'The draft was not created. Your entries remain available to review.'; },
    }));
  }

  label(value: string): string { return value.replace(/_/g, ' ').replace(/\b\w/g, character => character.toUpperCase()); }
}
