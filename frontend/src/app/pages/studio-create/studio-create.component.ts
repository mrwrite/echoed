import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { forkJoin, Subscription } from 'rxjs';

import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { Project, Workspace } from '../../models/v2-platform.model';
import { V2PlatformService } from '../../services/v2-platform.service';

@Component({
  selector: 'app-studio-create',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, EchoLoadingStateComponent, EchoStatePanelComponent],
  templateUrl: './studio-create.component.html',
  styleUrl: './studio-create.component.scss',
})
export class StudioCreateComponent implements OnInit, OnDestroy {
  readonly contentTypes = ['course', 'learning_path', 'documentation_pack', 'onboarding_track', 'implementation_playbook', 'knowledge_portal', 'certification', 'resource_pack'];
  workspaces: Workspace[] = [];
  projects: Project[] = [];
  loading = true;
  failed = false;
  savingProject = false;
  savingContent = false;
  projectError = '';
  contentError = '';
  statusMessage = '';

  projectForm = { workspaceId: '', name: '', description: '' };
  contentForm = { workspaceId: '', projectId: '', type: 'course', title: '', description: '', visibility: 'draft' };
  private readonly subscriptions = new Subscription();

  constructor(private readonly platform: V2PlatformService, private readonly router: Router) {}

  ngOnInit(): void { this.load(); }
  ngOnDestroy(): void { this.subscriptions.unsubscribe(); }

  get availableProjects(): Project[] {
    return this.contentForm.workspaceId ? this.projects.filter(project => project.workspace_id === this.contentForm.workspaceId) : [];
  }

  load(): void {
    this.loading = true;
    this.failed = false;
    this.subscriptions.add(forkJoin({ workspaces: this.platform.getWorkspaces(), projects: this.platform.getProjects() }).subscribe({
      next: result => {
        this.workspaces = result.workspaces;
        this.projects = result.projects;
        const defaultWorkspace = this.workspaces[0]?.id || '';
        this.projectForm.workspaceId ||= defaultWorkspace;
        this.contentForm.workspaceId ||= defaultWorkspace;
        this.loading = false;
      },
      error: () => { this.failed = true; this.loading = false; },
    }));
  }

  createProject(): void {
    if (!this.projectForm.workspaceId || !this.projectForm.name.trim() || this.savingProject) return;
    this.savingProject = true;
    this.projectError = '';
    this.statusMessage = '';
    this.subscriptions.add(this.platform.createProject({
      workspace_id: this.projectForm.workspaceId,
      name: this.projectForm.name.trim(),
      description: this.projectForm.description.trim() || null,
      status: 'active',
    }).subscribe({
      next: project => {
        this.projects = [...this.projects, project];
        this.contentForm.workspaceId = project.workspace_id;
        this.contentForm.projectId = project.id;
        this.projectForm = { workspaceId: project.workspace_id, name: '', description: '' };
        this.savingProject = false;
        this.statusMessage = `Project “${project.name}” created.`;
      },
      error: () => { this.savingProject = false; this.projectError = 'The project was not created. Your entries remain available to review.'; },
    }));
  }

  createContent(): void {
    if (!this.contentForm.workspaceId || !this.contentForm.title.trim() || this.savingContent) return;
    this.savingContent = true;
    this.contentError = '';
    this.statusMessage = '';
    this.subscriptions.add(this.platform.createProduct({
      workspace_id: this.contentForm.workspaceId,
      project_id: this.contentForm.projectId || null,
      product_type: this.contentForm.type,
      title: this.contentForm.title.trim(),
      description: this.contentForm.description.trim() || null,
      status: 'draft',
      review_state: 'draft',
      access_state: 'private',
      visibility: this.contentForm.visibility,
      pricing_model: 'internal',
    }).subscribe({
      next: product => { this.savingContent = false; this.router.navigate(['/studio/content', product.id]); },
      error: () => { this.savingContent = false; this.contentError = 'The learning offering was not created. Your entries remain available to review.'; },
    }));
  }

  workspaceChanged(): void { this.contentForm.projectId = ''; }
  label(value: string): string { return value.replace(/_/g, ' ').replace(/\b\w/g, character => character.toUpperCase()); }
}
